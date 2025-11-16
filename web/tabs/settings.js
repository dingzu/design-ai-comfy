export function renderSettings(container) {
  container.innerHTML = '';

  const wrapper = document.createElement('div');
  wrapper.style.cssText = `
    padding: 20px;
    color: #e0e0e0;
  `;

  const title = document.createElement('h2');
  title.textContent = '插件配置';
  title.style.cssText = `
    margin: 0 0 20px 0;
    font-size: 20px;
    font-weight: 600;
    color: #ffffff;
  `;
  wrapper.appendChild(title);

  const section = document.createElement('div');
  section.style.cssText = `
    background: #2a2a2a;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
  `;

  const sectionTitle = document.createElement('h3');
  sectionTitle.textContent = '数据管理';
  sectionTitle.style.cssText = `
    margin: 0 0 16px 0;
    font-size: 16px;
    font-weight: 600;
    color: #ffffff;
  `;
  section.appendChild(sectionTitle);

  const actions = [
    {
      id: 'reset_onboarding',
      label: '重置所有新人引导',
      description: '清除所有引导记录，重新显示引导提示',
      buttonText: '重置引导',
      color: '#ff4444',
      hoverColor: '#cc0000',
      action: () => {
        if (confirm("确定要重置所有引导吗？这将清除所有已显示的引导记录。")) {
          localStorage.removeItem('designai_onboarding');
          alert("引导已重置！请刷新页面查看效果。");
          location.reload();
        }
      }
    },
    {
      id: 'export_tasks',
      label: '导出本地任务',
      description: '导出所有本地保存的任务数据到 JSON 文件',
      buttonText: '导出任务',
      color: '#28a745',
      hoverColor: '#218838',
      action: () => {
        try {
          const taskData = localStorage.getItem('workflow_tasks');

          if (!taskData) {
            alert("没有找到本地任务数据！");
            return;
          }

          const tasks = JSON.parse(taskData);

          if (!Array.isArray(tasks) || tasks.length === 0) {
            alert("没有找到本地任务数据！");
            return;
          }

          const exportData = {
            version: "1.0",
            exportTime: new Date().toISOString(),
            taskCount: tasks.length,
            tasks: tasks
          };

          const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `designai_tasks_${new Date().toISOString().split('T')[0]}.json`;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          URL.revokeObjectURL(url);

          console.log(`✅ 已导出 ${tasks.length} 个任务`);
          alert(`成功导出 ${tasks.length} 个任务！`);
        } catch (error) {
          console.error("导出任务失败:", error);
          alert("导出任务失败，请查看控制台了解详情。");
        }
      }
    },
    {
      id: 'import_tasks',
      label: '导入本地任务',
      description: '从 JSON 文件导入任务数据',
      buttonText: '导入任务',
      color: '#007bff',
      hoverColor: '#0056b3',
      action: () => {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'application/json';
        input.onchange = async (e) => {
          try {
            const file = e.target.files[0];
            if (!file) return;

            const text = await file.text();
            const importData = JSON.parse(text);

            if (!importData.tasks || !Array.isArray(importData.tasks)) {
              alert("无效的任务数据格式！");
              return;
            }

            const confirmMsg = `确定要导入 ${importData.tasks.length} 个任务吗？\n导出时间: ${importData.exportTime}\n注意：这将覆盖现有的本地任务！`;
            if (!confirm(confirmMsg)) {
              return;
            }

            try {
              localStorage.setItem('workflow_tasks', JSON.stringify(importData.tasks));
              console.log(`✅ 成功导入 ${importData.tasks.length} 个任务`);
              alert(`成功导入 ${importData.tasks.length} 个任务！`);
            } catch (error) {
              console.error("导入任务失败:", error);
              alert("导入任务失败，可能是存储空间不足。");
            }
          } catch (error) {
            console.error("导入任务失败:", error);
            alert("导入任务失败，请确保文件格式正确。");
          }
        };
        input.click();
      }
    },
    {
      id: 'clear_tasks',
      label: '清理本地任务',
      description: '清除所有本地保存的任务数据',
      buttonText: '清理任务',
      color: '#dc3545',
      hoverColor: '#c82333',
      action: () => {
        try {
          const taskData = localStorage.getItem('workflow_tasks');

          if (!taskData) {
            alert("本地没有任务数据！");
            return;
          }

          const tasks = JSON.parse(taskData);
          const taskCount = Array.isArray(tasks) ? tasks.length : 0;

          if (taskCount === 0) {
            alert("本地没有任务数据！");
            return;
          }

          const confirmMsg = `确定要清除所有本地任务吗？\n当前共有 ${taskCount} 个任务\n注意：此操作不可恢复！`;
          if (!confirm(confirmMsg)) {
            return;
          }

          localStorage.removeItem('workflow_tasks');
          console.log(`✅ 已清除 ${taskCount} 个任务`);
          alert(`成功清除 ${taskCount} 个任务！`);
        } catch (error) {
          console.error("清理任务失败:", error);
          alert("清理任务失败，请查看控制台了解详情。");
        }
      }
    }
  ];

  actions.forEach(actionConfig => {
    const actionItem = document.createElement('div');
    actionItem.style.cssText = `
      margin-bottom: 16px;
      padding-bottom: 16px;
      border-bottom: 1px solid #404040;
    `;

    const actionLabel = document.createElement('div');
    actionLabel.textContent = actionConfig.label;
    actionLabel.style.cssText = `
      font-size: 14px;
      font-weight: 500;
      color: #ffffff;
      margin-bottom: 4px;
    `;

    const actionDesc = document.createElement('div');
    actionDesc.textContent = actionConfig.description;
    actionDesc.style.cssText = `
      font-size: 12px;
      color: #a0a0a0;
      margin-bottom: 12px;
    `;

    const actionButton = document.createElement('button');
    actionButton.textContent = actionConfig.buttonText;
    actionButton.style.cssText = `
      width: 100%;
      padding: 10px;
      background: ${actionConfig.color};
      color: white;
      border: none;
      border-radius: 6px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
    `;

    actionButton.addEventListener('mouseenter', () => {
      actionButton.style.background = actionConfig.hoverColor;
    });

    actionButton.addEventListener('mouseleave', () => {
      actionButton.style.background = actionConfig.color;
    });

    actionButton.addEventListener('click', actionConfig.action);

    actionItem.appendChild(actionLabel);
    actionItem.appendChild(actionDesc);
    actionItem.appendChild(actionButton);
    section.appendChild(actionItem);
  });

  wrapper.appendChild(section);
  container.appendChild(wrapper);
}
