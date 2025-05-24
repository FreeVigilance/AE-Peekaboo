import logging
from datetime import timedelta
from typing import Optional

import jwt
from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from jwt import InvalidTokenError
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend, login_required
from starlette.responses import Response

from src.application.services.aho import AhoCorasickService
from src.application.services.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_refresh_token,
)
from src.infrastructure.models.public import (
    Drug,
    SubmissionRule,
    TypeOfEvent,
    User,
)
from src.infrastructure.repositories.drugs import DrugsRepo
from src.infrastructure.repositories.user import UserRepo
from src.infrastructure.session import async_session_factory
from src.interfaces.api.dependencies.session import get_session
from src.settings import settings

logger = logging.getLogger(__name__)


class DrugsAdmin(Admin):
    @login_required
    async def create(self, request: Request) -> Response:
        """Create model endpoint."""

        await self._create(request)

        identity = request.path_params["identity"]
        model_view = self._find_model_view(identity)
        if identity == "drug":
            Form = await model_view.scaffold_form(
                model_view._form_create_rules
            )
            form_data = await self._handle_form_data(request)
            form = Form(form_data)

            context = {
                "model_view": model_view,
                "form": form,
            }

            if request.method == "GET":
                return await self.templates.TemplateResponse(
                    request, model_view.create_template, context
                )

            if not form.validate():
                return await self.templates.TemplateResponse(
                    request,
                    model_view.create_template,
                    context,
                    status_code=400,
                )

            form_data_dict = self._denormalize_wtform_data(
                form.data, model_view.model
            )
            try:
                obj = await model_view.insert_model(request, form_data_dict)
                await AhoCorasickService.add_drug_to_automation(
                    self.app.state.automaton, obj
                )
                self.app.state.automaton.make_automaton()
            except Exception as e:
                logger.exception(e)
                context["error"] = str(e)
                return await self.templates.TemplateResponse(
                    request,
                    model_view.create_template,
                    context,
                    status_code=400,
                )

            url = self.get_save_redirect_url(
                request=request,
                form=form_data,
                obj=obj,
                model_view=model_view,
            )
            return RedirectResponse(url=url, status_code=302)
        if identity == "user":
            Form = await model_view.scaffold_form(
                model_view._form_create_rules
            )
            form_data = await self._handle_form_data(request)
            form = Form(form_data)

            context = {
                "model_view": model_view,
                "form": form,
            }

            if request.method == "GET":
                return await self.templates.TemplateResponse(
                    request, model_view.create_template, context
                )

            if not form.validate():
                return await self.templates.TemplateResponse(
                    request,
                    model_view.create_template,
                    context,
                    status_code=400,
                )

            form_data_dict = self._denormalize_wtform_data(
                form.data, model_view.model
            )
            form_data_dict["password"] = get_password_hash(
                form_data_dict["password"]
            )
            try:
                obj = await model_view.insert_model(request, form_data_dict)
            except Exception as e:
                logger.exception(e)
                context["error"] = str(e)
                return await self.templates.TemplateResponse(
                    request,
                    model_view.create_template,
                    context,
                    status_code=400,
                )

            url = self.get_save_redirect_url(
                request=request,
                form=form_data,
                obj=obj,
                model_view=model_view,
            )
            return RedirectResponse(url=url, status_code=302)
        return await super().create(request)

    @login_required
    async def delete(self, request: Request) -> Response:

        params = request.query_params.get("pks", "")
        pks = params.split(",") if params else []
        db_session = await anext(get_session())
        repo = DrugsRepo(db_session)
        for pk in pks:
            obj = await repo.get(id=pk)
            try:
                self.app.state.automaton.pop(obj.trade_name)
            except KeyError:
                pass
            try:
                self.app.state.automaton.pop(obj.inn)
            except KeyError:
                pass
        self.app.state.automaton.make_automaton()
        return await super().delete(request)


class DrugAdmin(ModelView, model=Drug):
    column_list = [column for column in Drug.__table__.columns]
    column_searchable_list = [
        Drug.trade_name,
        Drug.inn,
    ]
    column_details_exclude_list = [Drug.submission_rules]
    column_formatters = {
        Drug.trade_name: lambda m, a: (
            m.trade_name[:50] + "..."
            if len(m.trade_name) > 50
            else m.trade_name
        ),
    }
    page_size = 15
    form_excluded_columns = ["submission_rules"]


class SubmissionAdmin(ModelView, model=SubmissionRule):
    column_exclude_list = [SubmissionRule.id]
    column_searchable_list = [
        "drug.trade_name",
        "drug.inn",
        SubmissionRule.routename,
        SubmissionRule.source_countries,
        SubmissionRule.receiver,
        SubmissionRule.type_of_event,
        SubmissionRule.deadline_to_submit,
    ]
    column_formatters = {
        SubmissionRule.receiver: lambda m, a: (
            m.receiver[:50] + "..." if len(m.receiver) > 50 else m.receiver
        ),
    }
    page_size = 15

    form_ajax_refs = {
        "drug": {
            "fields": ["id", "trade_name", "inn"],
        },
        "event_types": {
            "fields": [
                "id",
                "name",
            ],
        },
    }


class TypeOfEventAdmin(ModelView, model=TypeOfEvent):
    column_list = [column for column in TypeOfEvent.__table__.columns]
    column_searchable_list = [
        column for column in TypeOfEvent.__table__.columns
    ]

    page_size = 15

    form_ajax_refs = {
        "submission_rule": {
            "fields": ["id"],
        },
    }


class UserAdmin(ModelView, model=User):
    column_list = [User.email, User.is_admin]
    column_searchable_list = [User.email, User.is_admin]

    page_size = 15


class SQLAdminAuthenticationBackend(AuthenticationBackend):
    def __init__(self, secret_key: str):
        super().__init__(secret_key=secret_key)
        self.secret_key = secret_key

    async def login(self, request: Request) -> bool:
        """Handle login by validating credentials and storing tokens in session."""
        form_data = await request.form()
        oauth_form = OAuth2PasswordRequestForm(
            username=form_data.get("username"),
            password=form_data.get("password"),
            scope="",
        )
        async with async_session_factory() as db_session:
            repo = UserRepo(db_session)
            try:
                user = await authenticate_user(
                    oauth_form.username, oauth_form.password, repo
                )
            except:
                return False
            await db_session.close()
        if not user or user.is_admin is False:
            return False

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(data={"sub": user.email})

        request.session["access_token"] = access_token
        request.session["refresh_token"] = refresh_token
        request.session["user_email"] = user.email

        return True

    async def logout(self, request: Request) -> bool:
        """Clear the session to log out the user."""
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> Optional[Response]:
        """Validate the access token for each request."""
        access_token = request.session.get("access_token")
        refresh_token = request.session.get("refresh_token")

        if not access_token:
            return RedirectResponse(url="/admin/login", status_code=302)
        async with async_session_factory() as db_session:
            repo = UserRepo(db_session)

            try:
                payload = jwt.decode(
                    access_token,
                    settings.app.secret_key,
                    algorithms=[ALGORITHM],
                )
                email = payload.get("sub")
                if email is None:
                    return RedirectResponse(
                        url="/admin/login", status_code=302
                    )

                user = await repo.get(email=email)
                if user is None:
                    return RedirectResponse(
                        url="/admin/login", status_code=302
                    )
                await db_session.close()
                return True

            except InvalidTokenError:
                if not refresh_token:
                    return RedirectResponse(
                        url="/admin/login", status_code=302
                    )

                try:
                    user = await verify_refresh_token(refresh_token, repo)
                    access_token_expires = timedelta(
                        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
                    )
                    new_access_token = create_access_token(
                        data={"sub": user.email},
                        expires_delta=access_token_expires,
                    )
                    request.session["access_token"] = new_access_token
                    await db_session.close()

                    return True

                except HTTPException:
                    await db_session.close()

                    return RedirectResponse(
                        url="/admin/login", status_code=302
                    )
