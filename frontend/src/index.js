import React from 'react';
import ReactDOM from 'react-dom/client';
import { AdaptivityProvider, ConfigProvider } from '@vkontakte/vkui';
import '@vkontakte/vkui/dist/vkui.css';
import bridge from '@vkontakte/vk-bridge';

import App from './App';

// Инициализация VK Bridge
bridge.send('VKWebAppInit');

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <ConfigProvider>
    <AdaptivityProvider>
      <App />
    </AdaptivityProvider>
  </ConfigProvider>
); 