// 模拟环境标识
export const isSimulation = true;

// 模拟 ComfyUI 的 app 对象
export const app = {
    extensions: [],
    
    // 注册扩展的方法
    registerExtension(extension) {
        console.log('📦 Registering extension:', extension.name);
        this.extensions.push(extension);

        // 注册设置
        if (extension.settings) {
            console.log('⚙️ Registering settings for extension:', extension.name);
            extension.settings.forEach(settingConfig => {
                this.extensionManager.setting.register(settingConfig);
            });
        }

        // 模拟扩展的生命周期
        if (extension.setup) {
            // 延迟执行 setup，模拟真实环境
            setTimeout(() => {
                console.log('🚀 Setting up extension:', extension.name);
                extension.setup();
            }, 100);
        }

        console.log('✅ Extension registered successfully:', extension.name);
    },
    
    // 模拟其他可能需要的方法
    getExtensions() {
        return this.extensions;
    },
    
    // 模拟画布相关方法
    canvas: {
        getContext() {
            return document.createElement('canvas').getContext('2d');
        }
    },
    
    // 模拟图对象
    graph: {
        nodes: [],
        onAfterChange: null
    },

    // 加载工作流数据
    loadGraphData(workflowData) {
        try {
            console.log('📂 Loading workflow data...');

            // 解析工作流数据（如果是字符串）
            let data = workflowData;
            if (typeof workflowData === 'string') {
                data = JSON.parse(workflowData);
            }

            // 验证数据格式
            if (!data || typeof data !== 'object') {
                throw new Error('Invalid workflow data format');
            }

            // 清空当前图
            this.graph.nodes = [];

            // 加载节点数据
            if (data.nodes) {
                this.graph.nodes = data.nodes;
                console.log(`✅ Loaded ${data.nodes.length} nodes`);
            }

            // 触发图更新事件
            if (this.graph.onAfterChange) {
                this.graph.onAfterChange();
            }

            console.log('✅ Workflow loaded successfully');
            return true;
        } catch (error) {
            console.error('❌ Failed to load workflow:', error);
            throw error;
        }
    },

    // 将图转换为 prompt 格式（模拟方法，返回固定测试数据）
    async graphToPrompt() {
        console.log('🔄 Converting graph to prompt format...');

        const prompt = {
            output: {
                "3": {
                  
                    class_type: "KSampler",
                    inputs: {
                        seed: 156680208700286,
                        steps: 20,
                        cfg: 8.0,
                        sampler_name: "euler",
                        scheduler: "normal",
                        denoise: 1.0,
                        model: ["4", 0],
                        positive: ["6", 0],
                        negative: ["7", 0],
                        latent_image: ["5", 0]
                    }
                },
                "4": {
                    class_type: "CheckpointLoaderSimple",
                    inputs: {
                        ckpt_name: "v1-5-pruned-emaonly.safetensors"
                    }
                },
                "5": {
                    class_type: "EmptyLatentImage",
                    inputs: {
                        width: 512,
                        height: 512,
                        batch_size: 1
                    }
                },
                "6": {
                    class_type: "CLIPTextEncode",
                    inputs: {
                        text: "beautiful landscape, mountains, sunset, dramatic lighting",
                        clip: ["4", 1]
                    }
                },
                "7": {
                    class_type: "CLIPTextEncode",
                    inputs: {
                        text: "text, watermark, low quality, blurry",
                        clip: ["4", 1]
                    }
                },
                "8": {
                    class_type: "VAEDecode",
                    inputs: {
                        samples: ["3", 0],
                        vae: ["4", 2]
                    }
                },
                "9": {
                    class_type: "SaveImage",
                    inputs: {
                        filename_prefix: "ComfyUI",
                        images: ["8", 0]
                    }
                }
            },
            workflow: {
                config: {},
                extra: {
                    ds: {
                        scale: 1.0,
                        offset: [0, 0]
                    }
                },
                groups: [],
                last_link_id: 9,
                last_node_id: 9,
                links: [
                    [1, 4, 0, 3, 0, "MODEL"],
                    [2, 5, 0, 3, 3, "LATENT"],
                    [3, 4, 1, 6, 0, "CLIP"],
                    [4, 6, 0, 3, 1, "CONDITIONING"],
                    [5, 4, 1, 7, 0, "CLIP"],
                    [6, 7, 0, 3, 2, "CONDITIONING"],
                    [7, 3, 0, 8, 0, "LATENT"],
                    [8, 4, 2, 8, 1, "VAE"],
                    [9, 8, 0, 9, 0, "IMAGE"]
                ],
                nodes: [
                    {
                        id: 3,
                        type: "KSampler",
                        pos: [863, 186],
                        size: [315, 262],
                        flags: {},
                        order: 3,
                        mode: 0,
                        inputs: [
                            { name: "model", type: "MODEL", link: 1 },
                            { name: "positive", type: "CONDITIONING", link: 4 },
                            { name: "negative", type: "CONDITIONING", link: 6 },
                            { name: "latent_image", type: "LATENT", link: 2 }
                        ],
                        outputs: [
                            {
                                name: "LATENT",
                                type: "LATENT",
                                links: [7],
                                shape: 3,
                                slot_index: 0
                            }
                        ],
                        properties: { "Node name for S&R": "KSampler" },
                        widgets_values: [156680208700286, "randomize", 20, 8, "euler", "normal", 1]
                    },
                    {
                        id: 4,
                        type: "CheckpointLoaderSimple",
                        pos: [26, 474],
                        size: [315, 98],
                        flags: {},
                        order: 0,
                        mode: 0,
                        outputs: [
                            {
                                name: "MODEL",
                                type: "MODEL",
                                links: [1],
                                shape: 3,
                                slot_index: 0
                            },
                            {
                                name: "CLIP",
                                type: "CLIP",
                                links: [3, 5],
                                shape: 3,
                                slot_index: 1
                            },
                            {
                                name: "VAE",
                                type: "VAE",
                                links: [8],
                                shape: 3,
                                slot_index: 2
                            }
                        ],
                        properties: { "Node name for S&R": "CheckpointLoaderSimple" },
                        widgets_values: ["v1-5-pruned-emaonly.safetensors"]
                    },
                    {
                        id: 5,
                        type: "EmptyLatentImage",
                        pos: [473, 609],
                        size: [315, 106],
                        flags: {},
                        order: 1,
                        mode: 0,
                        outputs: [
                            {
                                name: "LATENT",
                                type: "LATENT",
                                links: [2],
                                shape: 3,
                                slot_index: 0
                            }
                        ],
                        properties: { "Node name for S&R": "EmptyLatentImage" },
                        widgets_values: [512, 512, 1]
                    },
                    {
                        id: 6,
                        type: "CLIPTextEncode",
                        pos: [415, 186],
                        size: [400, 200],
                        flags: {},
                        order: 2,
                        mode: 0,
                        inputs: [
                            { name: "clip", type: "CLIP", link: 3 }
                        ],
                        outputs: [
                            {
                                name: "CONDITIONING",
                                type: "CONDITIONING",
                                links: [4],
                                shape: 3,
                                slot_index: 0
                            }
                        ],
                        properties: { "Node name for S&R": "CLIPTextEncode" },
                        widgets_values: ["beautiful landscape, mountains, sunset, dramatic lighting"]
                    },
                    {
                        id: 7,
                        type: "CLIPTextEncode",
                        pos: [415, 389],
                        size: [400, 200],
                        flags: {},
                        order: 2,
                        mode: 0,
                        inputs: [
                            { name: "clip", type: "CLIP", link: 5 }
                        ],
                        outputs: [
                            {
                                name: "CONDITIONING",
                                type: "CONDITIONING",
                                links: [6],
                                shape: 3,
                                slot_index: 0
                            }
                        ],
                        properties: { "Node name for S&R": "CLIPTextEncode" },
                        widgets_values: ["text, watermark, low quality, blurry"]
                    },
                    {
                        id: 8,
                        type: "VAEDecode",
                        pos: [1209, 188],
                        size: [210, 46],
                        flags: {},
                        order: 4,
                        mode: 0,
                        inputs: [
                            { name: "samples", type: "LATENT", link: 7 },
                            { name: "vae", type: "VAE", link: 8 }
                        ],
                        outputs: [
                            {
                                name: "IMAGE",
                                type: "IMAGE",
                                links: [9],
                                shape: 3,
                                slot_index: 0
                            }
                        ],
                        properties: { "Node name for S&R": "VAEDecode" }
                    },
                    {
                        id: 9,
                        type: "SaveImage",
                        pos: [1451, 189],
                        size: [315, 270],
                        flags: {},
                        order: 5,
                        mode: 0,
                        inputs: [
                            { name: "images", type: "IMAGE", link: 9 }
                        ],
                        properties: {},
                        widgets_values: ["ComfyUI"]
                    }
                ],
                version: 0.4
            }
        };

        console.log('✅ Graph converted to prompt format');
        return prompt;
    },
    
    // 模拟扩展管理器
    extensionManager: {
        sidebarTabs: [],
        settings: new Map(),
        settingCategories: new Map(),
        
        // 注册侧边栏标签页
        registerSidebarTab(config) {
            console.log('📋 Registering sidebar tab:', config.id);
            
            // 验证必需参数
            if (!config.id || !config.title || !config.type || !config.render) {
                console.error('❌ Missing required parameters for sidebar tab');
                return;
            }
            
            // 检查ID是否已存在
            if (this.sidebarTabs.find(tab => tab.id === config.id)) {
                console.error('❌ Sidebar tab with ID already exists:', config.id);
                return;
            }
            
            // 添加到侧边栏标签页列表
            this.sidebarTabs.push(config);
            
            // 创建侧边栏UI（如果还不存在）
            this.createSidebarUI();
            
            // 创建标签页
            this.createSidebarTab(config);
            
            console.log('✅ Sidebar tab registered successfully:', config.id);
        },
        
        // 创建侧边栏UI
        createSidebarUI() {
            if (document.getElementById('comfyui-sidebar')) {
                return; // 已存在
            }
            
            const sidebar = document.createElement('div');
            sidebar.id = 'comfyui-sidebar';
            sidebar.style.cssText = `
                position: fixed;
                top: 0;
                right: 0;
                width: 300px;
                height: 100vh;
                background: #1a1a1a;
                border-left: 2px solid #404040;
                box-shadow: -5px 0 15px rgba(0, 0, 0, 0.5);
                z-index: 9998;
                display: flex;
                flex-direction: column;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            `
            
            // 创建标签页头部
            const tabHeader = document.createElement('div');
            tabHeader.id = 'sidebar-tab-header';
            tabHeader.style.cssText = `
                display: flex;
                background: #1a1a1a;
                border-bottom: 1px solid #404040;
                overflow-x: auto;
                min-height: 50px;
            `
            
            // 创建内容区域
            const tabContent = document.createElement('div');
            tabContent.id = 'sidebar-tab-content';
            tabContent.style.cssText = `
                flex: 1;
                overflow-y: auto;
                padding: 0;
            `;
            
            sidebar.appendChild(tabHeader);
            sidebar.appendChild(tabContent);
            document.body.appendChild(sidebar);
            
            console.log('🎨 Sidebar UI created');
        },
        
        // 创建单个标签页
        createSidebarTab(config) {
            const tabHeader = document.getElementById('sidebar-tab-header');
            const tabContent = document.getElementById('sidebar-tab-content');
            
            // 创建标签页按钮
        const tabButton = document.createElement('button');
        tabButton.id = `tab-button-${config.id}`;
        tabButton.style.cssText = `
            padding: 12px 16px;
            border: none;
            background: transparent;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            color: #a0a0a0;
            border-bottom: 3px solid transparent;
            transition: all 0.2s ease;
            white-space: nowrap;
            display: flex;
            align-items: center;
            gap: 8px;
        `
        
        // 添加图标（如果有）
        if (config.icon) {
            const icon = document.createElement('i');
            icon.className = config.icon;
            icon.style.cssText = `
                font-size: 18px;
                color: #ffffff;
                background: #2a2a2a;
                border-radius: 50%;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
            `
            tabButton.appendChild(icon);
        }
            
            // 添加标题
            const title = document.createElement('span');
            title.textContent = config.title;
            tabButton.appendChild(title);
            
            // 添加tooltip（如果有）
            if (config.tooltip) {
                tabButton.title = config.tooltip;
            }
            
            // 创建内容面板
            const contentPanel = document.createElement('div');
            contentPanel.id = `tab-content-${config.id}`;
            contentPanel.style.cssText = `
                display: none;
                height: 100%;
                padding: 0;
                overflow-y: auto;
            `
            
            // 渲染内容
            if (config.render) {
                config.render(contentPanel);
            }
            
            // 点击事件
            tabButton.addEventListener('click', () => {
                this.activateTab(config.id);
            });
            
            // 悬停效果
            tabButton.addEventListener('mouseenter', () => {
                if (!tabButton.classList.contains('active')) {
                    tabButton.style.backgroundColor = '#2a2a2a';
                    tabButton.style.color = '#e0e0e0';
                }
            });

            tabButton.addEventListener('mouseleave', () => {
                if (!tabButton.classList.contains('active')) {
                    tabButton.style.backgroundColor = 'transparent';
                    tabButton.style.color = '#a0a0a0';
                }
            })
            
            tabHeader.appendChild(tabButton);
            tabContent.appendChild(contentPanel);
            
            // 如果是第一个标签页，自动激活
            if (this.sidebarTabs.length === 1) {
                this.activateTab(config.id);
            }
        },
        
        // 激活指定标签页
        activateTab(tabId) {
            // 重置所有标签页按钮
            const allButtons = document.querySelectorAll('[id^="tab-button-"]');
            allButtons.forEach(button => {
                button.classList.remove('active');
                button.style.backgroundColor = 'transparent';
                button.style.color = '#a0a0a0';
                button.style.borderBottomColor = 'transparent';
            })
            
            // 隐藏所有内容面板
            const allPanels = document.querySelectorAll('[id^="tab-content-"]');
            allPanels.forEach(panel => {
                panel.style.display = 'none';
            });
            
            // 激活指定标签页
            const activeButton = document.getElementById(`tab-button-${tabId}`);
            const activePanel = document.getElementById(`tab-content-${tabId}`);
            
            if (activeButton && activePanel) {
                activeButton.classList.add('active');
                activeButton.style.backgroundColor = 'transparent';
                activeButton.style.color = '#ffffff';
                activeButton.style.borderBottomColor = '#ffffff';

                activePanel.style.display = 'block';

                console.log('🎯 Activated sidebar tab:', tabId);
            }
        },

        // 设置管理 API
        setting: {
            parent: null,

            init(parent) {
                this.parent = parent;
            },

            // 注册设置项
            register(settingConfig) {
                if (!settingConfig.id) {
                    console.error('❌ Setting must have an id');
                    return;
                }

                const setting = {
                    id: settingConfig.id,
                    name: settingConfig.name || settingConfig.id,
                    type: settingConfig.type || 'text',
                    defaultValue: settingConfig.defaultValue,
                    options: settingConfig.options || [],
                    attrs: settingConfig.attrs || {},
                    category: settingConfig.category || 'General',
                    tooltip: settingConfig.tooltip || '',
                    onChange: settingConfig.onChange || null,
                    callback: settingConfig.callback || null,
                };

                // 存储设置定义
                this.parent.settings.set(setting.id, setting);

                // 添加到分类
                if (!this.parent.settingCategories.has(setting.category)) {
                    this.parent.settingCategories.set(setting.category, []);
                }
                this.parent.settingCategories.get(setting.category).push(setting);

                // 从 localStorage 加载值或使用默认值
                const storedValue = localStorage.getItem(`setting.${setting.id}`);
                if (storedValue !== null) {
                    try {
                        setting.value = JSON.parse(storedValue);
                    } catch (e) {
                        setting.value = storedValue;
                    }
                } else {
                    setting.value = setting.defaultValue;
                }

                console.log('⚙️ Registered setting:', setting.id);
                return setting;
            },

            // 获取设置值
            get(id) {
                const setting = this.parent.settings.get(id);
                if (!setting) {
                    console.warn(`⚠️ Setting not found: ${id}`);
                    return undefined;
                }
                return setting.value;
            },

            // 设置值
            async set(id, value) {
                const setting = this.parent.settings.get(id);
                if (!setting) {
                    console.error(`❌ Setting not found: ${id}`);
                    return false;
                }

                const oldValue = setting.value;
                setting.value = value;

                // 保存到 localStorage
                try {
                    localStorage.setItem(`setting.${id}`, JSON.stringify(value));
                } catch (e) {
                    localStorage.setItem(`setting.${id}`, value);
                }

                // 触发 onChange 回调
                if (setting.onChange) {
                    try {
                        await setting.onChange(value, oldValue);
                    } catch (e) {
                        console.error(`❌ Error in onChange callback for ${id}:`, e);
                    }
                }

                console.log(`✅ Setting updated: ${id} = ${value}`);
                return true;
            },

            // 获取所有设置
            getAll() {
                return Array.from(this.parent.settings.values());
            },

            // 获取分类设置
            getByCategory(category) {
                return this.parent.settingCategories.get(category) || [];
            },

            // 获取所有分类
            getCategories() {
                return Array.from(this.parent.settingCategories.keys());
            }
        }
    }
};

// 初始化设置管理器
app.extensionManager.setting.init(app.extensionManager);

// 模拟全局对象
window.app = app;

console.log('🎯 ComfyUI app simulation loaded');