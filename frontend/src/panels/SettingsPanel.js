import React, { useState, useEffect, useContext } from 'react';
import {
  Panel,
  PanelHeader,
  Group,
  Cell,
  Switch,
  Div,
  Button,
  Text,
  Title,
  Spinner
} from '@vkontakte/vkui';
import {
  Icon28NotificationOutline,
  Icon28SettingsOutline,
  Icon28InfoOutline
} from '@vkontakte/icons';
import { UserContext } from '../contexts/UserContext';

const SettingsPanel = ({ id, go }) => {
  const { user, showSnackbar } = useContext(UserContext);
  const [settings, setSettings] = useState({
    notifications_enabled: true
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) {
      setSettings({
        notifications_enabled: user.notifications_enabled
      });
    }
  }, [user]);

  const handleToggleNotifications = async (enabled) => {
    try {
      setLoading(true);
      // Здесь должен быть API вызов для обновления настроек
      setSettings({ ...settings, notifications_enabled: enabled });
      showSnackbar('Настройки обновлены', 'success');
    } catch (error) {
      showSnackbar('Ошибка обновления настроек', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Panel id={id}>
      <PanelHeader>Настройки</PanelHeader>

      {/* Уведомления */}
      <Group header={<Title level="3">Уведомления</Title>}>
        <Cell
          before={<Icon28NotificationOutline />}
          after={
            <Switch
              checked={settings.notifications_enabled}
              onChange={(e) => handleToggleNotifications(e.target.checked)}
              disabled={loading}
            />
          }
        >
          Получать уведомления
        </Cell>
        
        <Cell>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Text>Уведомлений сегодня</Text>
            <Text weight="semibold">{user?.notifications_sent_today || 0} / 10</Text>
          </div>
        </Cell>
      </Group>

      {/* Информация о подписке */}
      <Group header={<Title level="3">Подписка</Title>}>
        <Cell>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Text>Текущий тариф</Text>
            <Text weight="semibold">
              {user?.subscription_type === 'free' && 'Бесплатно'}
              {user?.subscription_type === 'basic' && 'Базовый'}
              {user?.subscription_type === 'standard' && 'Стандарт'}
              {user?.subscription_type === 'premium' && 'Премиум'}
            </Text>
          </div>
        </Cell>
        
        <Cell>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Text>Лимит групп</Text>
            <Text weight="semibold">{user?.max_groups || 1}</Text>
          </div>
        </Cell>
        
        {user?.subscription_expires && (
          <Cell>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Text>Истекает</Text>
              <Text weight="semibold">
                {new Date(user.subscription_expires).toLocaleDateString()}
              </Text>
            </div>
          </Cell>
        )}
        
        <Cell>
          <Button
            mode="primary"
            size="l"
            stretched
            onClick={() => go('billing')}
          >
            Управление подпиской
          </Button>
        </Cell>
      </Group>

      {/* О приложении */}
      <Group header={<Title level="3">О приложении</Title>}>
        <Cell before={<Icon28InfoOutline />}>
          <div>
            <Text weight="semibold">Плагиат-Детектор</Text>
            <Text style={{ color: 'var(--vkui--color_text_secondary)' }}>
              Версия 1.0.0
            </Text>
          </div>
        </Cell>
        
        <Cell>
          <Text style={{ fontSize: '14px', color: 'var(--vkui--color_text_secondary)' }}>
            Автоматический поиск плагиата контента в группах ВКонтакте. 
            Мониторинг происходит 2 раза в день (09:00 и 18:00).
          </Text>
        </Cell>
      </Group>

      {/* Статистика */}
      <Group header={<Title level="3">Статистика</Title>}>
        <Cell>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Text>Всего найдено плагиата</Text>
            <Text weight="semibold">{user?.total_plagiarism_found || 0}</Text>
          </div>
        </Cell>
        
        <Cell>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Text>Последнее уведомление</Text>
            <Text weight="semibold">
              {user?.last_notification_date 
                ? new Date(user.last_notification_date).toLocaleDateString()
                : 'Нет'
              }
            </Text>
          </div>
        </Cell>
      </Group>
    </Panel>
  );
};

export default SettingsPanel; 