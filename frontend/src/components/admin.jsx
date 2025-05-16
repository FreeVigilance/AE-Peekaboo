import { useNavigate } from 'react-router-dom';

function MyComponent() {
    const navigate = useNavigate();

    const goToAdmin = () => {
        window.location.href = 'http://localhost:8000/admin';
    };

    return <button onClick={goToAdmin}>В админку</button>;
}

export default MyComponent;