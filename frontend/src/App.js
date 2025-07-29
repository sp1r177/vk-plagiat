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
      // Проверяем, запущено ли приложение в VK
      const isVKApp = window.location.href.includes('vk.com') || 
                      window.location.href.includes('vk-apps.com');
      
      if (isVKApp) {
        // Получаем данные пользователя из VK
        const userData = await bridge.send('VKWebAppGetUserInfo');
        
        // Авторизуемся в нашем API
        const authResult = await AuthService.vkLogin(userData.id);
        
        if (authResult.success) {
          setUser(authResult.user);
        } else {
          showSnackbar('Ошибка авторизации', 'error');
        }
      } else {
        // Демо режим для GitHub Pages
        setUser({
          id: 1,
          vk_id: 123456789,
          first_name: "Демо",
          last_name: "Пользователь",
          photo_url: "https://vk.com/images/camera_200.png",
          subscription_type: "premium",
          subscription_expires: "2024-12-31T00:00:00Z",
          notifications_enabled: true,
          max_groups: 10,
          total_plagiarism_found: 15,
          notifications_sent_today: 3,
          last_notification_date: "2024-01-15T10:30:00Z"
        });
      }
    } catch (error) {
      console.error('Ошибка инициализации:', error);
      // В демо режиме показываем тестового пользователя
      setUser({
        id: 1,
        vk_id: 123456789,
        first_name: "Демо",
        last_name: "Пользователь",
        photo_url: "https://vk.com/images/camera_200.png",
        subscription_type: "premium",
        subscription_expires: "2024-12-31T00:00:00Z",
        notifications_enabled: true,
        max_groups: 10,
        total_plagiarism_found: 15,
        notifications_sent_today: 3,
        last_notification_date: "2024-01-15T10:30:00Z"
      });
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