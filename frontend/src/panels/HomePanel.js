import React, { useState, useEffect, useContext } from 'react';
import {
  Panel,
  PanelHeader,
  Group,
  Card,
  CardGrid,
  Title,
  Text,
  Button,
  Div,
  Avatar,
  Cell,
  Badge,
  Progress,
  Spinner
} from '@vkontakte/vkui';
import {
  Icon28SearchOutline,
  Icon28UsersOutline,
  Icon28SettingsOutline,
  Icon28WalletOutline,
  Icon28HistoryOutline,
  Icon28CheckCircleOutline,
  Icon28WarningTriangleOutline
} from '@vkontakte/icons';
import { UserContext } from '../contexts/UserContext';
import GroupsService from '../services/GroupsService';
import MonitoringService from '../services/MonitoringService';

const HomePanel = ({ id, go }) => {
  const { user, showSnackbar } = useContext(UserContext);
  const [stats, setStats] = useState(null);
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Загружаем группы пользователя
      const groupsResult = await GroupsService.getUserGroups();
      if (groupsResult.success) {
        setGroups(groupsResult.groups);
      }

      // Загружаем статистику мониторинга
      const statsResult = await MonitoringService.getStatistics();
      if (statsResult.success) {
        setStats(statsResult.stats);
      }
    } catch (error) {
      showSnackbar('Ошибка загрузки данных', 'error');
    } finally {
      setLoading(false);
    }
  };

  const getSubscriptionColor = () => {
    switch (user?.subscription_type) {
      case 'premium': return 'var(--vkui--color_background_accent_themed)';
      case 'standard': return 'var(--vkui--color_background_positive)';
      case 'basic': return 'var(--vkui--color_background_warning)';
      default: return 'var(--vkui--color_background_negative)';
    }
  };

  const getSubscriptionName = (type) => {
    const names = {
      'free': 'Бесплатно',
      'basic': 'Базовый',
      'standard': 'Стандарт',
      'premium': 'Премиум'
    };
    return names[type] || type;
  };

  if (loading) {
    return (
      <Panel id={id}>
        <PanelHeader>Плагиат-Детектор</PanelHeader>
        <Group>
          <Div style={{ textAlign: 'center', padding: '50px 0' }}>
            <Spinner size="large" />
            <Text style={{ marginTop: '16px' }}>Загрузка данных...</Text>
          </Div>
        </Group>
      </Panel>
    );
  }

  return (
    <Panel id={id}>
      <PanelHeader>Плагиат-Детектор</PanelHeader>
      
      {/* Информация о пользователе */}
      <Group>
        <Card mode="shadow">
          <Div>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '16px' }}>
              <Avatar size={48} src={user?.photo_url} />
              <div style={{ marginLeft: '12px', flex: 1 }}>
                <Title level="3" weight="semibold">
                  {user?.first_name} {user?.last_name}
                </Title>
                <Text style={{ color: 'var(--vkui--color_text_secondary)' }}>
                  Подписка: {getSubscriptionName(user?.subscription_type)}
                </Text>
              </div>
              <Badge
                style={{ backgroundColor: getSubscriptionColor() }}
                mode="prominent"
              >
                {user?.max_groups} групп
              </Badge>
            </div>
            
            {user?.subscription_expires && (
              <div style={{ marginTop: '12px' }}>
                <Text style={{ fontSize: '14px', color: 'var(--vkui--color_text_secondary)' }}>
                  Подписка истекает: {new Date(user.subscription_expires).toLocaleDateString()}
                </Text>
              </div>
            )}
          </Div>
        </Card>
      </Group>

      {/* Статистика */}
      {stats && (
        <Group header={<Title level="3">Статистика</Title>}>
          <CardGrid size="l">
            <Card mode="shadow">
              <Div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <Text style={{ fontSize: '24px', fontWeight: 'bold' }}>
                      {stats.total_plagiarism_found}
                    </Text>
                    <Text style={{ color: 'var(--vkui--color_text_secondary)' }}>
                      Найдено плагиата
                    </Text>
                  </div>
                  <Icon28WarningTriangleOutline width={32} height={32} />
                </div>
              </Div>
            </Card>
            
            <Card mode="shadow">
              <Div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <Text style={{ fontSize: '24px', fontWeight: 'bold' }}>
                      {stats.total_posts_checked}
                    </Text>
                    <Text style={{ color: 'var(--vkui--color_text_secondary)' }}>
                      Проверено постов
                    </Text>
                  </div>
                  <Icon28CheckCircleOutline width={32} height={32} />
                </div>
              </Div>
            </Card>
          </CardGrid>
        </Group>
      )}

      {/* Быстрые действия */}
      <Group header={<Title level="3">Быстрые действия</Title>}>
        <Cell
          before={<Icon28UsersOutline />}
          after={<Badge mode="prominent">{groups.length}</Badge>}
          onClick={() => go('groups')}
        >
          Мои группы
        </Cell>
        
        <Cell
          before={<Icon28SearchOutline />}
          onClick={() => go('monitoring')}
        >
          Запустить мониторинг
        </Cell>
        
        <Cell
          before={<Icon28HistoryOutline />}
          onClick={() => go('history')}
        >
          История плагиата
        </Cell>
        
        <Cell
          before={<Icon28WalletOutline />}
          onClick={() => go('billing')}
        >
          Тарифы и оплата
        </Cell>
        
        <Cell
          before={<Icon28SettingsOutline />}
          onClick={() => go('settings')}
        >
          Настройки
        </Cell>
      </Group>

      {/* Прогресс использования */}
      <Group header={<Title level="3">Использование</Title>}>
        <Div>
          <div style={{ marginBottom: '12px' }}>
            <Text>Группы: {groups.length} / {user?.max_groups}</Text>
          </div>
          <Progress
            value={(groups.length / user?.max_groups) * 100}
            style={{ marginBottom: '16px' }}
          />
          
          <div style={{ marginBottom: '12px' }}>
            <Text>Уведомления сегодня: {user?.notifications_sent_today} / 10</Text>
          </div>
          <Progress
            value={(user?.notifications_sent_today / 10) * 100}
          />
        </Div>
      </Group>
    </Panel>
  );
};

export default HomePanel; 