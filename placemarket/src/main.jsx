import { createRoot } from 'react-dom/client'
import { Provider } from 'react-redux';
import './style/index.css'
import App from './components/App.jsx'
import store from './store/store.js';

createRoot(document.getElementById('root')).render(
  <Provider store={store}>
    <App />
  </Provider>,
);
