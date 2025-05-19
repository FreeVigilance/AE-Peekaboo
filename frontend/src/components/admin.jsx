import { useNavigate } from 'react-router-dom';

function MyComponent() {
    const navigate = useNavigate();

    const goToAdmin = () => {
        window.location.href = `${process.env.REACT_APP_API_URL}/admin`;
    };

    return <button onClick={goToAdmin}>В админку</button>;
}

export default MyComponent;