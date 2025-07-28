import React, { useState, useEffect, useContext } from 'react';
import {
  Panel,
  PanelHeader,
  Group,
  Cell,
  Div,
  Text,
  Title,
  Badge,
  Spinner,
  Button,
  Card,
  CardGrid
} from '@vkontakte/vkui';
import {
  Icon28HistoryOutline,
  Icon28WarningTriangleOutline,
  Icon28ExternalOutline
} from '@vkontakte/icons';
import { UserContext } from '../contexts/UserContext';

const HistoryPanel = ({ id, go }) => {
  const { user, showSnackbar } = useContext(UserContext);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    loadHistory();
    loadStats();
  }, []);

  const loadHistory = async () => {
    try {
      setLoading(true);
      // Здесь должен быть API вызов для получения истории
      const mockHistory = [
        {
          id: 1,
          created_at: '2024-01-15T10:30:00Z',
          overall_similarity: 0.85,
          text_similarity: 0.90,
          image_similarity: 0.75,
          original_post_url: 'https://vk.com/wall-123456_789',
          plagiarized_post_url: 'https://vk.com/wall-654321_987',
          group_name: 'Тестовая группа'
        },
        {
          id: 2,
          created_at: '2024-01-14T15:45:00Z',
          overall_similarity: 0.72,
          text_similarity: 0.68,
          image_similarity: 0.80,
          original_post_url: 'https://vk.com/wall-123456_790',
          plagiarized_post_url: 'https://vk.com/wall-654321_988',
          group_name: 'Другая группа'
        }
      ];
      setHistory(mockHistory);
    } catch (error) {
      showSnackbar('Ошибка загрузки истории', 'error');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      // Здесь должен быть API вызов для получения статистики
      const mockStats = {
        today: 2,
        week: 8,
        month: 25,
        total: 42
      };
      setStats(mockStats);
    } catch (error) {
      showSnackbar('Ошибка загрузки статистики', 'error');
    }
  };

  const openPost = (url) => {
    window.open(url, '_blank');
  };

  const getSimilarityColor = (similarity) => {
    if (similarity >= 0.8) return 'var(--vkui--color_background_negative)';
    if (similarity >= 0.6) return 'var(--vkui--color_background_warning)';
    return 'var(--vkui--color_background_positive)';
  };

  if (loading) {
    return (
      <Panel id={id}>
        <PanelHeader>История плагиата</PanelHeader>
        <Group>
          <Div style={{ textAlign: 'center', padding: '50px 0' }}>
            <Spinner size="large" />
            <Text style={{ marginTop: '16px' }}>Загрузка истории...</Text>
          </Div>
        </Group>
      </Panel>
    );
  }

  return (
    <Panel id={id}>
      <PanelHeader>История плагиата</PanelHeader>

      {/* Статистика */}
      {stats && (
        <Group header={<Title level="3">Статистика</Title>}>
          <CardGrid size="l">
            <Card mode="shadow">
              <Div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <Text style={{ fontSize: '24px', fontWeight: 'bold' }}>
                      {stats.today}
                    </Text>
                    <Text style={{ color: 'var(--vkui--color_text_secondary)' }}>
                      Сегодня
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
                      {stats.week}
                    </Text>
                    <Text style={{ color: 'var(--vkui--color_text_secondary)' }}>
                      За неделю
                    </Text>
                  </div>
                  <Icon28HistoryOutline width={32} height={32} />
                </div>
              </Div>
            </Card>
          </CardGrid>
        </Group>
      )}

      {/* История */}
      <Group header={<Title level="3">Найденные случаи</Title>}>
        {history.length === 0 ? (
          <Div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Icon28HistoryOutline width={64} height={64} style={{ opacity: 0.5 }} />
            <Text style={{ color: 'var(--vkui--color_text_secondary)', marginTop: '16px' }}>
              Пока не найдено случаев плагиата
            </Text>
          </Div>
        ) : (
          history.map((item) => (
            <Card key={item.id} mode="shadow" style={{ marginBottom: '12px' }}>
              <Div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                  <div>
                    <Text weight="semibold">{item.group_name}</Text>
                    <Text style={{ fontSize: '12px', color: 'var(--vkui--color_text_secondary)' }}>
                      {new Date(item.created_at).toLocaleDateString()}
                    </Text>
                  </div>
                  <Badge
                    mode="prominent"
                    style={{ backgroundColor: getSimilarityColor(item.overall_similarity) }}
                  >
                    {Math.round(item.overall_similarity * 100)}%
                  </Badge>
                </div>
                
                <div style={{ marginBottom: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <Text style={{ fontSize: '14px' }}>Текст:</Text>
                    <Text style={{ fontSize: '14px', fontWeight: 'semibold' }}>
                      {Math.round(item.text_similarity * 100)}%
                    </Text>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Text style={{ fontSize: '14px' }}>Изображения:</Text>
                    <Text style={{ fontSize: '14px', fontWeight: 'semibold' }}>
                      {Math.round(item.image_similarity * 100)}%
                    </Text>
                  </div>
                </div>
                
                <div style={{ display: 'flex', gap: '8px' }}>
                  <Button
                    mode="secondary"
                    size="s"
                    before={<Icon28ExternalOutline />}
                    onClick={() => openPost(item.original_post_url)}
                  >
                    Оригинал
                  </Button>
                  <Button
                    mode="secondary"
                    size="s"
                    before={<Icon28ExternalOutline />}
                    onClick={() => openPost(item.plagiarized_post_url)}
                  >
                    Плагиат
                  </Button>
                </div>
              </Div>
            </Card>
          ))
        )}
      </Group>

      {/* Дополнительная информация */}
      <Group header={<Title level="3">Информация</Title>}>
        <Cell>
          <Text style={{ fontSize: '14px', color: 'var(--vkui--color_text_secondary)' }}>
            • История обновляется автоматически после каждого мониторинга
          </Text>
        </Cell>
        <Cell>
          <Text style={{ fontSize: '14px', color: 'var(--vkui--color_text_secondary)' }}>
            • Процент схожести рассчитывается по тексту и изображениям
          </Text>
        </Cell>
        <Cell>
          <Text style={{ fontSize: '14px', color: 'var(--vkui--color_text_secondary)' }}>
            • Красный цвет = высокий риск плагиата (≥80%)
          </Text>
        </Cell>
      </Group>
    </Panel>
  );
};

export default HistoryPanel; 