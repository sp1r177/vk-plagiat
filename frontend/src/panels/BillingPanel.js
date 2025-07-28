import React, { useState, useEffect, useContext } from 'react';
import {
  Panel,
  PanelHeader,
  Group,
  Cell,
  Button,
  Div,
  Text,
  Title,
  Card,
  CardGrid,
  Badge,
  Spinner
} from '@vkontakte/vkui';
import {
  Icon28WalletOutline,
  Icon28CheckCircleOutline,
  Icon28WarningTriangleOutline
} from '@vkontakte/icons';
import { UserContext } from '../contexts/UserContext';

const BillingPanel = ({ id, go }) => {
  const { user, showSnackbar } = useContext(UserContext);
  const [subscriptions, setSubscriptions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSubscriptions();
  }, []);

  const loadSubscriptions = async () => {
    try {
      setLoading(true);
      // Здесь должен быть API вызов для получения тарифов
      const mockSubscriptions = [
        {
          type: 'free',
          name: 'Бесплатно',
          groups: 1,
          days: 1,
          price: 0,
          features: ['1 группа', '1 день', 'Базовые уведомления']
        },
        {
          type: 'basic',
          name: 'Базовый',
          groups: 1,
          days: 30,
          price: 299,
          features: ['1 группа', '30 дней', 'Полные уведомления']
        },
        {
          type: 'standard',
          name: 'Стандарт',
          groups: 5,
          days: 30,
          price: 799,
          features: ['5 групп', '30 дней', 'Приоритетная поддержка']
        },
        {
          type: 'premium',
          name: 'Премиум',
          groups: 10,
          days: 30,
          price: 1199,
          features: ['10 групп', '30 дней', 'VIP поддержка', 'Аналитика']
        }
      ];
      setSubscriptions(mockSubscriptions);
    } catch (error) {
      showSnackbar('Ошибка загрузки тарифов', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async (subscriptionType) => {
    try {
      // Здесь должен быть API вызов для создания платежа
      showSnackbar('Переход к оплате...', 'success');
      // В реальном приложении здесь будет вызов VK Pay
    } catch (error) {
      showSnackbar('Ошибка создания платежа', 'error');
    }
  };

  const getCurrentSubscription = () => {
    return subscriptions.find(sub => sub.type === user?.subscription_type);
  };

  if (loading) {
    return (
      <Panel id={id}>
        <PanelHeader>Тарифы и оплата</PanelHeader>
        <Group>
          <Div style={{ textAlign: 'center', padding: '50px 0' }}>
            <Spinner size="large" />
            <Text style={{ marginTop: '16px' }}>Загрузка тарифов...</Text>
          </Div>
        </Group>
      </Panel>
    );
  }

  return (
    <Panel id={id}>
      <PanelHeader>Тарифы и оплата</PanelHeader>

      {/* Текущая подписка */}
      {user && (
        <Group header={<Title level="3">Текущая подписка</Title>}>
          <Card mode="shadow">
            <Div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <Text weight="semibold" style={{ fontSize: '18px' }}>
                  {getCurrentSubscription()?.name || 'Бесплатно'}
                </Text>
                <Badge mode="prominent">
                  Активна
                </Badge>
              </div>
              
              <div style={{ marginBottom: '12px' }}>
                <Text style={{ color: 'var(--vkui--color_text_secondary)' }}>
                  Групп: {user.max_groups} | Дней: {getCurrentSubscription()?.days || 1}
                </Text>
              </div>
              
              {user.subscription_expires && (
                <Text style={{ fontSize: '14px', color: 'var(--vkui--color_text_secondary)' }}>
                  Истекает: {new Date(user.subscription_expires).toLocaleDateString()}
                </Text>
              )}
            </Div>
          </Card>
        </Group>
      )}

      {/* Доступные тарифы */}
      <Group header={<Title level="3">Доступные тарифы</Title>}>
        <CardGrid size="l">
          {subscriptions.map((subscription) => (
            <Card
              key={subscription.type}
              mode="shadow"
              style={{
                border: user?.subscription_type === subscription.type 
                  ? '2px solid var(--vkui--color_background_accent_themed)' 
                  : '1px solid var(--vkui--color_separator_primary)'
              }}
            >
              <Div>
                <div style={{ textAlign: 'center', marginBottom: '16px' }}>
                  <Text weight="semibold" style={{ fontSize: '20px' }}>
                    {subscription.name}
                  </Text>
                  
                  <div style={{ marginTop: '8px' }}>
                    {subscription.price === 0 ? (
                      <Text weight="bold" style={{ fontSize: '24px', color: 'var(--vkui--color_background_positive)' }}>
                        Бесплатно
                      </Text>
                    ) : (
                      <Text weight="bold" style={{ fontSize: '24px' }}>
                        {subscription.price}₽
                      </Text>
                    )}
                    <Text style={{ color: 'var(--vkui--color_text_secondary)' }}>
                      / {subscription.days} дней
                    </Text>
                  </div>
                </div>
                
                <div style={{ marginBottom: '16px' }}>
                  {subscription.features.map((feature, index) => (
                    <div key={index} style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
                      <Icon28CheckCircleOutline 
                        width={16} 
                        height={16} 
                        style={{ color: 'var(--vkui--color_background_positive)', marginRight: '8px' }}
                      />
                      <Text style={{ fontSize: '14px' }}>{feature}</Text>
                    </div>
                  ))}
                </div>
                
                {user?.subscription_type !== subscription.type && (
                  <Button
                    mode={subscription.price === 0 ? "secondary" : "primary"}
                    size="l"
                    stretched
                    onClick={() => handleSubscribe(subscription.type)}
                  >
                    {subscription.price === 0 ? 'Выбрать' : 'Подписаться'}
                  </Button>
                )}
                
                {user?.subscription_type === subscription.type && (
                  <Button
                    mode="tertiary"
                    size="l"
                    stretched
                    disabled
                  >
                    Текущий тариф
                  </Button>
                )}
              </Div>
            </Card>
          ))}
        </CardGrid>
      </Group>

      {/* Информация о платежах */}
      <Group header={<Title level="3">Информация</Title>}>
        <Cell>
          <Text style={{ fontSize: '14px', color: 'var(--vkui--color_text_secondary)' }}>
            • Платежи обрабатываются через VK Pay
          </Text>
        </Cell>
        <Cell>
          <Text style={{ fontSize: '14px', color: 'var(--vkui--color_text_secondary)' }}>
            • Подписка продлевается автоматически
          </Text>
        </Cell>
        <Cell>
          <Text style={{ fontSize: '14px', color: 'var(--vkui--color_text_secondary)' }}>
            • Можно отменить в любой момент
          </Text>
        </Cell>
      </Group>
    </Panel>
  );
};

export default BillingPanel; 