import React, { useState, useEffect, useContext } from 'react';
import {
  Panel,
  PanelHeader,
  Group,
  Cell,
  Button,
  Div,
  Avatar,
  Badge,
  Switch,
  FormItem,
  Input,
  ModalCard,
  ModalRoot,
  Spinner,
  Text,
  Title
} from '@vkontakte/vkui';
import {
  Icon28AddOutline,
  Icon28DeleteOutline,
  Icon28SettingsOutline,
  Icon28CheckCircleOutline,
  Icon28WarningTriangleOutline
} from '@vkontakte/icons';
import { UserContext } from '../contexts/UserContext';
import GroupsService from '../services/GroupsService';

const GroupsPanel = ({ id, go }) => {
  const { user, showSnackbar } = useContext(UserContext);
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [newGroupId, setNewGroupId] = useState('');
  const [settings, setSettings] = useState({
    check_text: true,
    check_images: true,
    exclude_reposts: true
  });

  useEffect(() => {
    loadGroups();
  }, []);

  const loadGroups = async () => {
    try {
      setLoading(true);
      const result = await GroupsService.getUserGroups();
      if (result.success) {
        setGroups(result.groups);
      } else {
        showSnackbar(result.error, 'error');
      }
    } catch (error) {
      showSnackbar('Ошибка загрузки групп', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleAddGroup = async () => {
    if (!newGroupId.trim()) {
      showSnackbar('Введите ID группы', 'error');
      return;
    }

    try {
      const groupData = {
        vk_group_id: parseInt(newGroupId),
        check_text: settings.check_text,
        check_images: settings.check_images,
        exclude_reposts: settings.exclude_reposts
      };

      const result = await GroupsService.addGroup(groupData);
      if (result.success) {
        showSnackbar('Группа успешно добавлена', 'success');
        setShowAddModal(false);
        setNewGroupId('');
        loadGroups();
      } else {
        showSnackbar(result.error, 'error');
      }
    } catch (error) {
      showSnackbar('Ошибка добавления группы', 'error');
    }
  };

  const handleDeleteGroup = async (groupId) => {
    try {
      const result = await GroupsService.deleteGroup(groupId);
      if (result.success) {
        showSnackbar('Группа удалена', 'success');
        loadGroups();
      } else {
        showSnackbar(result.error, 'error');
      }
    } catch (error) {
      showSnackbar('Ошибка удаления группы', 'error');
    }
  };

  const handleUpdateSettings = async () => {
    if (!selectedGroup) return;

    try {
      const result = await GroupsService.updateGroup(selectedGroup.id, settings);
      if (result.success) {
        showSnackbar('Настройки обновлены', 'success');
        setShowSettingsModal(false);
        loadGroups();
      } else {
        showSnackbar(result.error, 'error');
      }
    } catch (error) {
      showSnackbar('Ошибка обновления настроек', 'error');
    }
  };

  const openSettingsModal = (group) => {
    setSelectedGroup(group);
    setSettings({
      check_text: group.check_text,
      check_images: group.check_images,
      exclude_reposts: group.exclude_reposts
    });
    setShowSettingsModal(true);
  };

  if (loading) {
    return (
      <Panel id={id}>
        <PanelHeader>Мои группы</PanelHeader>
        <Group>
          <Div style={{ textAlign: 'center', padding: '50px 0' }}>
            <Spinner size="large" />
            <Text style={{ marginTop: '16px' }}>Загрузка групп...</Text>
          </Div>
        </Group>
      </Panel>
    );
  }

  return (
    <Panel id={id}>
      <PanelHeader>Мои группы</PanelHeader>

      {/* Информация о лимитах */}
      <Group>
        <Cell>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Text>Групп добавлено: {groups.length}</Text>
            <Badge mode="prominent">{user?.max_groups}</Badge>
          </div>
        </Cell>
      </Group>

      {/* Список групп */}
      <Group header={<Title level="3">Группы для мониторинга</Title>}>
        {groups.length === 0 ? (
          <Div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Text style={{ color: 'var(--vkui--color_text_secondary)' }}>
              У вас пока нет групп для мониторинга
            </Text>
            <Button
              mode="primary"
              size="l"
              style={{ marginTop: '16px' }}
              onClick={() => setShowAddModal(true)}
            >
              Добавить группу
            </Button>
          </Div>
        ) : (
          groups.map((group) => (
            <Cell
              key={group.id}
              before={<Avatar size={40} src={group.photo_url} />}
              after={
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Button
                    mode="tertiary"
                    size="s"
                    onClick={() => openSettingsModal(group)}
                  >
                    <Icon28SettingsOutline />
                  </Button>
                  <Button
                    mode="destructive"
                    size="s"
                    onClick={() => handleDeleteGroup(group.id)}
                  >
                    <Icon28DeleteOutline />
                  </Button>
                </div>
              }
            >
              <div>
                <Text weight="semibold">{group.name}</Text>
                <div style={{ display: 'flex', gap: '8px', marginTop: '4px' }}>
                  <Badge mode="prominent" size="s">
                    {group.posts_checked} постов
                  </Badge>
                  <Badge mode="destructive" size="s">
                    {group.plagiarism_found} плагиат
                  </Badge>
                </div>
                {group.last_check && (
                  <Text style={{ fontSize: '12px', color: 'var(--vkui--color_text_secondary)' }}>
                    Последняя проверка: {new Date(group.last_check).toLocaleDateString()}
                  </Text>
                )}
              </div>
            </Cell>
          ))
        )}
      </Group>

      {/* Кнопка добавления */}
      {groups.length > 0 && groups.length < user?.max_groups && (
        <Group>
          <Button
            mode="primary"
            size="l"
            before={<Icon28AddOutline />}
            onClick={() => setShowAddModal(true)}
            stretched
          >
            Добавить группу
          </Button>
        </Group>
      )}

      {/* Модальное окно добавления группы */}
      <ModalRoot activeModal={showAddModal ? 'add-group' : null}>
        <ModalCard
          id="add-group"
          header="Добавить группу"
          onClose={() => setShowAddModal(false)}
          actions={[
            {
              label: 'Отмена',
              mode: 'secondary',
              onClick: () => setShowAddModal(false)
            },
            {
              label: 'Добавить',
              mode: 'primary',
              onClick: handleAddGroup
            }
          ]}
        >
          <Div>
            <FormItem top="ID группы ВКонтакте">
              <Input
                value={newGroupId}
                onChange={(e) => setNewGroupId(e.target.value)}
                placeholder="Например: 123456"
                type="number"
              />
            </FormItem>
            
            <FormItem>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Text>Проверять текст</Text>
                  <Switch
                    checked={settings.check_text}
                    onChange={(e) => setSettings({ ...settings, check_text: e.target.checked })}
                  />
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Text>Проверять изображения</Text>
                  <Switch
                    checked={settings.check_images}
                    onChange={(e) => setSettings({ ...settings, check_images: e.target.checked })}
                  />
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Text>Исключать репосты</Text>
                  <Switch
                    checked={settings.exclude_reposts}
                    onChange={(e) => setSettings({ ...settings, exclude_reposts: e.target.checked })}
                  />
                </div>
              </div>
            </FormItem>
          </Div>
        </ModalCard>
      </ModalRoot>

      {/* Модальное окно настроек */}
      <ModalRoot activeModal={showSettingsModal ? 'group-settings' : null}>
        <ModalCard
          id="group-settings"
          header="Настройки группы"
          onClose={() => setShowSettingsModal(false)}
          actions={[
            {
              label: 'Отмена',
              mode: 'secondary',
              onClick: () => setShowSettingsModal(false)
            },
            {
              label: 'Сохранить',
              mode: 'primary',
              onClick: handleUpdateSettings
            }
          ]}
        >
          <Div>
            {selectedGroup && (
              <div style={{ marginBottom: '16px' }}>
                <Text weight="semibold">{selectedGroup.name}</Text>
              </div>
            )}
            
            <FormItem>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Text>Проверять текст</Text>
                  <Switch
                    checked={settings.check_text}
                    onChange={(e) => setSettings({ ...settings, check_text: e.target.checked })}
                  />
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Text>Проверять изображения</Text>
                  <Switch
                    checked={settings.check_images}
                    onChange={(e) => setSettings({ ...settings, check_images: e.target.checked })}
                  />
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Text>Исключать репосты</Text>
                  <Switch
                    checked={settings.exclude_reposts}
                    onChange={(e) => setSettings({ ...settings, exclude_reposts: e.target.checked })}
                  />
                </div>
              </div>
            </FormItem>
          </Div>
        </ModalCard>
      </ModalRoot>
    </Panel>
  );
};

export default GroupsPanel; 