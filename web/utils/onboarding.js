const ONBOARDING_STORAGE_KEY = 'designai_onboarding';

export class OnboardingManager {
  constructor() {
    this.onboardingSteps = new Map();
    this.loadState();
  }

  loadState() {
    try {
      const saved = localStorage.getItem(ONBOARDING_STORAGE_KEY);
      if (saved) {
        const data = JSON.parse(saved);
        this.onboardingSteps = new Map(Object.entries(data));
      }
    } catch (error) {
      console.error('Failed to load onboarding state:', error);
    }
  }

  saveState() {
    try {
      const data = Object.fromEntries(this.onboardingSteps);
      localStorage.setItem(ONBOARDING_STORAGE_KEY, JSON.stringify(data));
    } catch (error) {
      console.error('Failed to save onboarding state:', error);
    }
  }

  isCompleted(stepId) {
    return this.onboardingSteps.get(stepId) === true;
  }

  markCompleted(stepId) {
    this.onboardingSteps.set(stepId, true);
    this.saveState();
  }

  reset(stepId) {
    if (stepId) {
      this.onboardingSteps.delete(stepId);
    } else {
      this.onboardingSteps.clear();
    }
    this.saveState();
  }
}

export function createOnboardingDialog(config) {
  const { title, steps, onComplete, stepId } = config;

  const overlay = document.createElement('div');
  overlay.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.7);
    z-index: 100000;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: fadeIn 0.3s ease-out;
  `;

  const dialog = document.createElement('div');
  dialog.style.cssText = `
    background: #2a2a2a;
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    max-width: 600px;
    width: 90%;
    max-height: 80vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    animation: slideUp 0.3s ease-out;
  `;

  const header = document.createElement('div');
  header.style.cssText = `
    padding: 24px;
    border-bottom: 1px solid #404040;
    background: #1a1a1a;
  `;

  const titleEl = document.createElement('h2');
  titleEl.textContent = title;
  titleEl.style.cssText = `
    margin: 0;
    color: #ffffff;
    font-size: 20px;
    font-weight: 600;
  `;

  header.appendChild(titleEl);

  const content = document.createElement('div');
  content.style.cssText = `
    padding: 24px;
    overflow-y: auto;
    flex: 1;
  `;

  const checkboxStates = new Array(steps.length).fill(false);

  steps.forEach((step, index) => {
    const isImportantStep = step.includes('ComfyUI 无法运行绝大部分工作流');

    const stepContainer = document.createElement('div');
    stepContainer.style.cssText = `
      margin-bottom: ${index === steps.length - 1 ? '0' : '20px'};
      display: flex;
      align-items: flex-start;
      gap: 12px;
      ${isImportantStep ? `
        background: linear-gradient(135deg, #ff1744 0%, #ff5252 50%, #ff1744 100%);
        background-size: 200% 200%;
        padding: 20px;
        border-radius: 12px;
        border: 4px solid #ff0000;
        box-shadow:
          0 0 30px rgba(255, 23, 68, 0.8),
          0 0 60px rgba(255, 23, 68, 0.6),
          0 0 90px rgba(255, 23, 68, 0.4),
          inset 0 0 20px rgba(255, 255, 255, 0.2);
        animation:
          pulseGlow 1.5s ease-in-out infinite,
          backgroundMove 3s ease infinite,
          megaShake 4s ease-in-out infinite;
        position: relative;
        transform-origin: center;
      ` : ''}
    `;

    if (isImportantStep) {
      const warningOverlay = document.createElement('div');
      warningOverlay.style.cssText = `
        position: absolute;
        top: -10px;
        left: 50%;
        transform: translateX(-50%);
        background: #ffeb3b;
        color: #ff0000;
        padding: 4px 16px;
        border-radius: 20px;
        font-weight: 900;
        font-size: 14px;
        box-shadow: 0 4px 12px rgba(255, 235, 59, 0.6);
        animation: bounce 1s ease-in-out infinite;
        z-index: 10;
        letter-spacing: 2px;
      `;
      warningOverlay.textContent = '⚠️ 必读 ⚠️';
      stepContainer.appendChild(warningOverlay);
    }

    const checkboxWrapper = document.createElement('div');
    checkboxWrapper.style.cssText = `
      flex-shrink: 0;
      margin-top: 2px;
      ${isImportantStep ? 'animation: spin 3s linear infinite;' : ''}
    `;

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.id = `onboarding-step-${index}`;
    checkbox.style.cssText = `
      width: ${isImportantStep ? '28px' : '20px'};
      height: ${isImportantStep ? '28px' : '20px'};
      cursor: pointer;
      accent-color: ${isImportantStep ? '#ffeb3b' : '#2a7ae4'};
      ${isImportantStep ? 'filter: drop-shadow(0 0 8px #ffeb3b);' : ''}
    `;

    checkbox.addEventListener('change', (e) => {
      checkboxStates[index] = e.target.checked;
      updateButtonState();
    });

    checkboxWrapper.appendChild(checkbox);

    const labelWrapper = document.createElement('div');
    labelWrapper.style.cssText = `
      flex: 1;
    `;

    const label = document.createElement('label');
    label.htmlFor = `onboarding-step-${index}`;

    if (isImportantStep) {
      label.innerHTML = `
        <div style="
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 12px;
          justify-content: center;
        ">
          <i class="mdi mdi-alert-octagon" style="
            font-size: 36px;
            color: #ffeb3b;
            animation: rotateBlink 2s ease-in-out infinite;
            filter: drop-shadow(0 0 10px #ffeb3b);
          "></i>
          <span style="
            font-weight: 900;
            font-size: 22px;
            color: #ffffff;
            text-shadow:
              0 0 20px rgba(255, 235, 59, 1),
              0 0 40px rgba(255, 235, 59, 0.8),
              2px 2px 4px rgba(0, 0, 0, 0.9);
            letter-spacing: 2px;
            animation: textGlow 1.5s ease-in-out infinite;
          ">🔥 超级重要 🔥</span>
          <i class="mdi mdi-alert-octagon" style="
            font-size: 36px;
            color: #ffeb3b;
            animation: rotateBlink 2s ease-in-out infinite;
            filter: drop-shadow(0 0 10px #ffeb3b);
          "></i>
        </div>
        <div style="
          color: #ffffff;
          font-size: 19px;
          line-height: 2;
          font-weight: 700;
          text-shadow:
            2px 2px 6px rgba(0, 0, 0, 1),
            0 0 10px rgba(255, 255, 255, 0.5);
          text-align: center;
          padding: 8px;
          background: rgba(0, 0, 0, 0.3);
          border-radius: 8px;
          border: 2px solid rgba(255, 235, 59, 0.5);
        ">
          ${step}
        </div>
      `;
    } else {
      label.textContent = step;
    }

    label.style.cssText = `
      color: ${isImportantStep ? '#ffffff' : '#e0e0e0'};
      font-size: ${isImportantStep ? '19px' : '15px'};
      line-height: 1.6;
      cursor: pointer;
      display: block;
      user-select: none;
    `;

    labelWrapper.appendChild(label);

    stepContainer.appendChild(checkboxWrapper);
    stepContainer.appendChild(labelWrapper);

    content.appendChild(stepContainer);
  });

  const footer = document.createElement('div');
  footer.style.cssText = `
    padding: 20px 24px;
    border-top: 1px solid #404040;
    background: #1a1a1a;
    display: flex;
    justify-content: flex-end;
  `;

  const confirmButton = document.createElement('button');
  confirmButton.textContent = '我知道了';
  confirmButton.disabled = true;
  confirmButton.style.cssText = `
    padding: 10px 24px;
    background: #2a7ae4;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: not-allowed;
    transition: all 0.2s;
    opacity: 0.5;
  `;

  const updateButtonState = () => {
    const allChecked = checkboxStates.every(state => state === true);
    confirmButton.disabled = !allChecked;
    confirmButton.style.cursor = allChecked ? 'pointer' : 'not-allowed';
    confirmButton.style.opacity = allChecked ? '1' : '0.5';
    confirmButton.style.background = allChecked ? '#2a7ae4' : '#2a7ae4';
  };

  confirmButton.addEventListener('mouseenter', () => {
    if (!confirmButton.disabled) {
      confirmButton.style.background = '#1e5bb8';
    }
  });

  confirmButton.addEventListener('mouseleave', () => {
    if (!confirmButton.disabled) {
      confirmButton.style.background = '#2a7ae4';
    }
  });

  confirmButton.addEventListener('click', () => {
    if (!confirmButton.disabled) {
      overlay.style.animation = 'fadeOut 0.3s ease-out';
      setTimeout(() => {
        document.body.removeChild(overlay);
        if (onComplete) {
          onComplete();
        }
      }, 300);
    }
  });

  footer.appendChild(confirmButton);

  dialog.appendChild(header);
  dialog.appendChild(content);
  dialog.appendChild(footer);
  overlay.appendChild(dialog);

  const style = document.createElement('style');
  style.textContent = `
    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }
    @keyframes fadeOut {
      from { opacity: 1; }
      to { opacity: 0; }
    }
    @keyframes slideUp {
      from {
        transform: translateY(30px);
        opacity: 0;
      }
      to {
        transform: translateY(0);
        opacity: 1;
      }
    }
    @keyframes pulseGlow {
      0%, 100% {
        box-shadow:
          0 0 30px rgba(255, 23, 68, 0.8),
          0 0 60px rgba(255, 23, 68, 0.6),
          0 0 90px rgba(255, 23, 68, 0.4),
          inset 0 0 20px rgba(255, 255, 255, 0.2);
        transform: scale(1);
      }
      50% {
        box-shadow:
          0 0 50px rgba(255, 23, 68, 1),
          0 0 100px rgba(255, 23, 68, 0.8),
          0 0 150px rgba(255, 23, 68, 0.6),
          inset 0 0 30px rgba(255, 255, 255, 0.4);
        transform: scale(1.03);
      }
    }
    @keyframes backgroundMove {
      0% {
        background-position: 0% 50%;
      }
      50% {
        background-position: 100% 50%;
      }
      100% {
        background-position: 0% 50%;
      }
    }
    @keyframes megaShake {
      0%, 100% {
        transform: translateX(0) rotate(0deg);
      }
      10% {
        transform: translateX(-3px) rotate(-1deg);
      }
      20% {
        transform: translateX(3px) rotate(1deg);
      }
      30% {
        transform: translateX(-3px) rotate(-1deg);
      }
      40% {
        transform: translateX(3px) rotate(1deg);
      }
      50% {
        transform: translateX(-2px) rotate(0deg);
      }
      60% {
        transform: translateX(2px) rotate(0deg);
      }
      70% {
        transform: translateX(-2px) rotate(0deg);
      }
      80% {
        transform: translateX(2px) rotate(0deg);
      }
      90% {
        transform: translateX(0) rotate(0deg);
      }
    }
    @keyframes bounce {
      0%, 100% {
        transform: translateX(-50%) translateY(0);
      }
      50% {
        transform: translateX(-50%) translateY(-8px);
      }
    }
    @keyframes spin {
      0% {
        transform: rotate(0deg);
      }
      100% {
        transform: rotate(360deg);
      }
    }
    @keyframes rotateBlink {
      0%, 100% {
        opacity: 1;
        transform: rotate(0deg) scale(1);
      }
      25% {
        opacity: 0.5;
        transform: rotate(-15deg) scale(1.1);
      }
      50% {
        opacity: 1;
        transform: rotate(0deg) scale(1.2);
      }
      75% {
        opacity: 0.5;
        transform: rotate(15deg) scale(1.1);
      }
    }
    @keyframes textGlow {
      0%, 100% {
        text-shadow:
          0 0 20px rgba(255, 235, 59, 1),
          0 0 40px rgba(255, 235, 59, 0.8),
          2px 2px 4px rgba(0, 0, 0, 0.9);
      }
      50% {
        text-shadow:
          0 0 30px rgba(255, 235, 59, 1),
          0 0 60px rgba(255, 235, 59, 1),
          0 0 80px rgba(255, 235, 59, 0.8),
          2px 2px 4px rgba(0, 0, 0, 0.9);
      }
    }
  `;

  if (!document.getElementById('onboarding-animations')) {
    style.id = 'onboarding-animations';
    document.head.appendChild(style);
  }

  document.body.appendChild(overlay);
}

export function showFirstTimeOnboarding(manager) {
  const FIRST_TIME_STEP_ID = 'first_time_guide';

  if (!manager.isCompleted(FIRST_TIME_STEP_ID)) {
    createOnboardingDialog({
      title: '欢迎使用 DesignAI 插件',
      stepId: FIRST_TIME_STEP_ID,
      steps: [
        'DesignAI 插件存在于左侧边栏倒数第二个按钮。',
        '当前 ComfyUI 无法运行绝大部分工作流，请使用插件里的《在 DesignAI 运行当前工作流》功能。',
        '当前 ComfyUI 可以运行纯 CPU 的工作流。',
        '插件中有示例工作流以及 DesignAI 上的测试工作流可以加载和使用。'
      ],
      onComplete: () => {
        manager.markCompleted(FIRST_TIME_STEP_ID);
        console.log('✅ 首次引导完成');
      }
    });
  }
}

export function showRunWorkflowButtonGuide(manager, buttonElement) {
  const RUN_WORKFLOW_GUIDE_ID = 'run_workflow_button_guide';

  if (!manager.isCompleted(RUN_WORKFLOW_GUIDE_ID)) {
    const buttonRect = buttonElement.getBoundingClientRect();

    const spotlight = document.createElement('div');
    spotlight.style.cssText = `
      position: fixed;
      top: ${buttonRect.top}px;
      left: ${buttonRect.left}px;
      width: ${buttonRect.width}px;
      height: ${buttonRect.height}px;
      border: 4px solid #2a7ae4;
      border-radius: 6px;
      z-index: 100000;
      pointer-events: none;
      animation: pulse 2s ease-in-out infinite;
    `;

    const tooltip = document.createElement('div');
    tooltip.style.cssText = `
      position: fixed;
      top: ${buttonRect.bottom + 20}px;
      left: ${buttonRect.left + buttonRect.width / 2}px;
      transform: translateX(-50%);
      background: #2a2a2a;
      color: #ffffff;
      padding: 16px 20px;
      border-radius: 8px;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
      z-index: 100001;
      max-width: 350px;
      animation: slideUp 0.3s ease-out;
    `;

    const tooltipText = document.createElement('div');
    tooltipText.textContent = '点击这里可以将当前工作流运行在 DesignAI 服务器上';
    tooltipText.style.cssText = `
      font-size: 14px;
      line-height: 1.6;
      margin-bottom: 12px;
    `;

    const confirmButton = document.createElement('button');
    confirmButton.textContent = '我知道了';
    confirmButton.style.cssText = `
      width: 100%;
      padding: 8px 16px;
      background: #2a7ae4;
      color: white;
      border: none;
      border-radius: 6px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
    `;

    confirmButton.addEventListener('mouseenter', () => {
      confirmButton.style.background = '#1e5bb8';
    });

    confirmButton.addEventListener('mouseleave', () => {
      confirmButton.style.background = '#2a7ae4';
    });

    confirmButton.addEventListener('click', () => {
      spotlight.style.animation = 'fadeOut 0.3s ease-out';
      tooltip.style.animation = 'fadeOut 0.3s ease-out';

      setTimeout(() => {
        if (spotlight.parentNode) document.body.removeChild(spotlight);
        if (tooltip.parentNode) document.body.removeChild(tooltip);

        manager.markCompleted(RUN_WORKFLOW_GUIDE_ID);
        console.log('✅ 运行工作流按钮引导完成');
      }, 300);
    });

    tooltip.appendChild(tooltipText);
    tooltip.appendChild(confirmButton);

    const style = document.createElement('style');
    style.textContent = `
      @keyframes pulse {
        0%, 100% {
          border-width: 4px;
        }
        50% {
          border-width: 6px;
        }
      }
    `;

    if (!document.getElementById('spotlight-animations')) {
      style.id = 'spotlight-animations';
      document.head.appendChild(style);
    }

    document.body.appendChild(spotlight);
    document.body.appendChild(tooltip);
  }
}

export function showLoadWorkflowGuide(manager, buttonElement) {
  const LOAD_WORKFLOW_GUIDE_ID = 'load_workflow_guide';

  if (!manager.isCompleted(LOAD_WORKFLOW_GUIDE_ID)) {
    const buttonRect = buttonElement.getBoundingClientRect();

    const spotlight = document.createElement('div');
    spotlight.style.cssText = `
      position: fixed;
      top: ${buttonRect.top}px;
      left: ${buttonRect.left}px;
      width: ${buttonRect.width}px;
      height: ${buttonRect.height}px;
      border: 4px solid #2a7ae4;
      border-radius: 4px;
      z-index: 100000;
      pointer-events: none;
      animation: pulse 2s ease-in-out infinite;
    `;

    const tooltip = document.createElement('div');
    tooltip.style.cssText = `
      position: fixed;
      top: ${buttonRect.bottom + 20}px;
      left: ${buttonRect.left + buttonRect.width / 2}px;
      transform: translateX(-50%);
      background: #2a2a2a;
      color: #ffffff;
      padding: 16px 20px;
      border-radius: 8px;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
      z-index: 100001;
      max-width: 350px;
      animation: slideUp 0.3s ease-out;
    `;

    const tooltipText = document.createElement('div');
    tooltipText.textContent = '点击加载工作流！！';
    tooltipText.style.cssText = `
      font-size: 14px;
      line-height: 1.6;
      margin-bottom: 12px;
    `;

    const confirmButton = document.createElement('button');
    confirmButton.textContent = '我知道了';
    confirmButton.style.cssText = `
      width: 100%;
      padding: 8px 16px;
      background: #2a7ae4;
      color: white;
      border: none;
      border-radius: 6px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
    `;

    confirmButton.addEventListener('mouseenter', () => {
      confirmButton.style.background = '#1e5bb8';
    });

    confirmButton.addEventListener('mouseleave', () => {
      confirmButton.style.background = '#2a7ae4';
    });

    confirmButton.addEventListener('click', () => {
      spotlight.style.animation = 'fadeOut 0.3s ease-out';
      tooltip.style.animation = 'fadeOut 0.3s ease-out';

      setTimeout(() => {
        if (spotlight.parentNode) document.body.removeChild(spotlight);
        if (tooltip.parentNode) document.body.removeChild(tooltip);

        manager.markCompleted(LOAD_WORKFLOW_GUIDE_ID);
        console.log('✅ 加载工作流引导完成');
      }, 300);
    });

    tooltip.appendChild(tooltipText);
    tooltip.appendChild(confirmButton);

    const style = document.createElement('style');
    style.textContent = `
      @keyframes pulse {
        0%, 100% {
          border-width: 4px;
        }
        50% {
          border-width: 6px;
        }
      }
    `;

    if (!document.getElementById('spotlight-animations')) {
      style.id = 'spotlight-animations';
      document.head.appendChild(style);
    }

    document.body.appendChild(spotlight);
    document.body.appendChild(tooltip);
  }
}
