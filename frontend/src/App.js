import React, { useState, useEffect } from 'react';
import {
  AppRoot,
  SplitLayout,
  SplitCol,
  View,
  Panel,
  PanelHeader,
  usePlatform,
  ScreenSpinner,
  Snackbar
} from '@vkontakte/vkui';
import bridge from '@vkontakte/vk-bridge';

import HomePanel from './panels/HomePanel';
import GroupsPanel from './panels/GroupsPanel';
import SettingsPanel from './panels/SettingsPanel';
import BillingPanel from './panels/BillingPanel';
import HistoryPanel from './panels/HistoryPanel';
import AuthService from './services/AuthService';
import { UserContext } from './contexts/UserContext';

const App = () => {
  const platform = usePlatform();
  const [activePanel, setActivePanel] = useState('home');
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [snackbar, setSnackbar] = useState(null);

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      // Получаем данные пользователя из VK
      const userData = await bridge.send('VKWebAppGetUserInfo');
      
      // Авторизуемся в нашем API
      const authResult = await AuthService.vkLogin(userData.id);
      
      if (authResult.success) {
        setUser(authResult.user);
      } else {
        showSnackbar('Ошибка авторизации', 'error');
      }
    } catch (error) {
      console.error('Ошибка инициализации:', error);
      showSnackbar('Ошибка загрузки приложения', 'error');
    } finally {
      setLoading(false);
    }
  };

  const showSnackbar = (text, mode = 'success') => {
    setSnackbar(
      <Snackbar
        onClose={() => setSnackbar(null)}
        duration={4000}
        mode={mode}
      >
        {text}
      </Snackbar>
    );
  };

  const go = (panel) => {
    setActivePanel(panel);
  };

  if (loading) {
    return (
      <AppRoot>
        <ScreenSpinner size="large" />
      </AppRoot>
    );
  }

  return (
    <UserContext.Provider value={{ user, setUser, showSnackbar }}>
      <AppRoot>
        <SplitLayout header={<PanelHeader separator={false} />}>
          <SplitCol autoSpaced>
            <View activePanel={activePanel}>
              <HomePanel id="home" go={go} />
              <GroupsPanel id="groups" go={go} />
              <SettingsPanel id="settings" go={go} />
              <BillingPanel id="billing" go={go} />
              <HistoryPanel id="history" go={go} />
            </View>
          </SplitCol>
        </SplitLayout>
        {snackbar}
      </AppRoot>
    </UserContext.Provider>
  );
};

export default App; 