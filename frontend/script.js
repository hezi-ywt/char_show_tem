let currentCharacter = null;
let selectedImages = new Set();

// 检查用户是否已登录
function checkUser() {
    const userId = localStorage.getItem('userId');
    if (!userId) {
        document.getElementById('login-container').style.display = 'block';
        document.getElementById('main-container').style.display = 'none';
    } else {
        document.getElementById('login-container').style.display = 'none';
        document.getElementById('main-container').style.display = 'block';
        document.getElementById('current-user').textContent = userId;
        loadCharacter();
    }
}

// 设置用户
function setUser() {
    const userInput = document.getElementById('user-input').value.trim();
    if (userInput) {
        localStorage.setItem('userId', userInput);
        checkUser();
    } else {
        alert('请输入有效的标识！');
    }
}

// 重置用户
function resetUser() {
    localStorage.removeItem('userId');
    location.reload();
}

// 修改loadCharacter函数中的错误显示
async function loadCharacter() {
    try {
        const userId = localStorage.getItem('userId');
        const response = await fetch(`/api/character?user_id=${userId}`);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to load character');
        }
        currentCharacter = await response.json();
        displayCharacter();
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('main-container').innerHTML = `
            <div class="completion-message">
                <h2>评分完成！</h2>
                <p>用户 <strong>${localStorage.getItem('userId')}</strong> 已完成所有角色的评分</p>
                <div class="action-buttons">
                    <button onclick="resetUser()" class="primary-button">切换用户</button>
                    <button onclick="showRatingHistory()" class="secondary-button">查看历史记录</button>
                </div>
            </div>
        `;
    }
}

function displayCharacter() {
    const characterInfo = document.getElementById('character-info');
    const imagesContainer = document.getElementById('images-container');
    
    // 处理别名数组
    const getAliasesString = (aliases) => {
        if (!aliases || !Array.isArray(aliases) || aliases.length === 0) return '无';
        return aliases.join('、');
    };
    
    characterInfo.innerHTML = `
        <h2>${currentCharacter.中文名 || currentCharacter.character}</h2>
        <div class="character-info-grid">
            <div class="info-item">
                <label>Danbooru Tag：</label>
                <span>${currentCharacter.character}</span>
            </div>
            <div class="info-item">
                <label>英文名：</label>
                <span>${currentCharacter.英文名 || '未知'}</span>
            </div>
            <div class="info-item">
                <label>中文别名：</label>
                <span>${getAliasesString(currentCharacter.中文别名)}</span>
            </div>
            <div class="info-item">
                <label>英文别名：</label>
                <span>${getAliasesString(currentCharacter.英文别名)}</span>
            </div>
            <div class="info-item">
                <label>出处：</label>
                <span>${currentCharacter.出处中文名} (${currentCharacter.出处英文名})</span>
            </div>
            <div class="info-item">
                <label>性别：</label>
                <span>${currentCharacter.性别 || '未知'}</span>
            </div>
            <div class="info-item">
                <label>年龄：</label>
                <span>${currentCharacter.年龄 || '未知'}</span>
            </div>
        </div>
        <div class="character-description">
            ${currentCharacter.性格 ? `
                <div class="description-section">
                    <h3>性格特点</h3>
                    <p>${currentCharacter.性格}</p>
                </div>
            ` : ''}
            ${currentCharacter.兴趣 ? `
                <div class="description-section">
                    <h3>兴趣爱好</h3>
                    <p>${currentCharacter.兴趣}</p>
                </div>
            ` : ''}
            ${currentCharacter.职业和身份 ? `
                <div class="description-section">
                    <h3>职业和身份</h3>
                    <p>${currentCharacter.职业和身份}</p>
                </div>
            ` : ''}
            ${currentCharacter.角色详细介绍 ? `
                <div class="description-section">
                    <h3>角色介绍</h3>
                    <p>${currentCharacter.角色详细介绍}</p>
                </div>
            ` : ''}
        </div>
    `;
    
    // 显示图片部分
    const characterFolder = currentCharacter.character;
    
    // 创建图片显示函数
    const createImageGrid = (images, type, baseFolder) => {
        return images.length > 0 ? 
            `<div class="image-section">
                <h3>${type === 'face' ? '脸部图片' : '全身图片'}</h3>
                <div class="images-grid">
                    ${images.map(image => {
                        const imageUrl = `/static/${baseFolder}/${characterFolder}/${image}`;
                        // 检查图片是否在selectedImages集合中
                        const isSelected = selectedImages.has(imageUrl);
                        return `
                            <div class="image-card ${isSelected ? 'selected' : ''}" 
                                 onclick="selectImage('${imageUrl}', '${type}')">
                                <img src="${imageUrl}" 
                                     alt="${currentCharacter.character}"
                                     onerror="this.onerror=null; this.src='/static/placeholder.jpg';">
                                <div class="selection-overlay">
                                    <span class="checkmark">✓</span>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>` : '';
    };
    
    // 显示两种图片
    imagesContainer.innerHTML = `
        ${createImageGrid(currentCharacter.face_images || [], 'face', 'character_images_face')}
        ${createImageGrid(currentCharacter.full_body_images || [], 'full', 'character_images')}
    `;
}

function selectImage(imagePath, type) {
    const card = event.currentTarget;
    if (selectedImages.has(imagePath)) {
        selectedImages.delete(imagePath);
        card.classList.remove('selected');
    } else {
        selectedImages.add(imagePath);
        card.classList.add('selected');
    }
    // 更新选择计数
    document.getElementById('selected-count').textContent = selectedImages.size;
}

async function submitSelection() {
    if (selectedImages.size === 0) {
        alert('请至少选择一张图片！');
        return;
    }
    
    // 获取当前选择的图片
    const selectedFileNames = Array.from(selectedImages).map(url => {
        const parts = url.split('/');
        const type = parts[2].includes('face') ? 'face' : 'full';
        return {
            filename: parts.pop(),
            type: type
        };
    });
    
    // 更新当前角色的selected_images
    currentCharacter.selected_images = selectedFileNames;
    
    const ratingData = {
        character_id: currentCharacter.character,
        selected_images: selectedFileNames,
        user_id: localStorage.getItem('userId')
    };
    
    try {
        const editingRatingId = localStorage.getItem('editingRatingId');
        const url = editingRatingId ? 
            `/api/ratings/${editingRatingId}` : 
            '/api/rate';
        
        const response = await fetch(url, {
            method: editingRatingId ? 'PUT' : 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(ratingData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '提交失败');
        }
        
        // 清除选择和编辑状态
        selectedImages.clear();
        document.getElementById('selected-count').textContent = '0';
        localStorage.removeItem('editingRatingId');
        
        // 返回历史记录页面
        if (editingRatingId) {
            showRatingHistory();
        } else {
            loadCharacter();
        }
    } catch (error) {
        console.error('Error submitting selection:', error);
        alert('提交失败，请重试！' + error.message);
    }
}

async function loadCharacterDetails(characterName) {
    try {
        const response = await fetch(`/api/character/details?character_id=${characterName}`);
        if (!response.ok) {
            throw new Error('Character not found');
        }
        const character = await response.json();
        displayCharacterDetails(character);
    } catch (error) {
        console.error('Error loading character details:', error);
    }
}

function displayCharacterDetails(character) {
    const detailsContainer = document.getElementById('character-details');
    detailsContainer.innerHTML = `
        <h2>${character.中文名} (${character.英文名})</h2>
        <p>性别: ${character.性别}</p>
        <p>年龄: ${character.年龄}</p>
        <p>性格: ${character.性格}</p>
        <p>兴趣: ${character.兴趣}</p>
        <p>职业和身份: ${character.职业和身份}</p>
        <p>角色详细介绍: ${character.角色详细介绍}</p>
    `;
}

// 页面加载时检查用户
document.addEventListener('DOMContentLoaded', checkUser); 

// 示例调用
loadCharacterDetails('hishi_miracle_(umamusume)'); 

// 添加重置用户功能
function resetUser() {
    localStorage.removeItem('userId');
    location.reload();
} 

// 添加显示历史记录的函数
async function showRatingHistory() {
    const userId = localStorage.getItem('userId');
    try {
        const response = await fetch(`/api/ratings/${userId}`);
        if (!response.ok) {
            throw new Error('Failed to load ratings');
        }
        let ratings = await response.json();
        
        // 对评分记录进行排序，优先显示同时具有脸部和全身图片的角色
        ratings.sort((a, b) => {
            const aHasBoth = a.selected_images.some(img => img.type === 'face') && a.selected_images.some(img => img.type === 'full');
            const bHasBoth = b.selected_images.some(img => img.type === 'face') && b.selected_images.some(img => img.type === 'full');
            return bHasBoth - aHasBoth; // bHasBoth为true时排在前面
        });

        document.getElementById('main-container').innerHTML = `
            <div class="history-container">
                <h2>评分历史</h2>
                <button onclick="showRatingInterface()" class="primary-button">返回评分</button>
                <div class="ratings-grid">
                    ${ratings.map(character => {
                        console.log('Rating:', character); // 调试用
                        return `
                        <div class="rating-card">
                            <h3>${character.中文名 || character.character}</h3>
                            <p class="rating-time">评分时间: ${new Date(character.rating_time).toLocaleString()}</p>
                            <div class="selected-images">
                                <h4>已选择的图片：</h4>
                                ${character.selected_images.map(img => {
                                    console.log('Image:', img); // 调试用
                                    if (!img || !img.filename) return '';
                                    const baseFolder = img.type === 'face' ? 'character_images_face' : 'character_images';
                                    const imgPath = `/static/${baseFolder}/${character.character}/${img.filename}`;
                                    console.log('Image path:', imgPath); // 调试用
                                    return `
                                        <img src="${imgPath}" 
                                             alt="${character.character}"
                                             class="thumbnail"
                                             onerror="this.onerror=null; this.src='/static/placeholder.jpg';">
                                    `;
                                }).join('')}
                            </div>
                            <button onclick="editRating('${character.character}')" class="secondary-button">重新编辑</button>
                        </div>
                    `}).join('')}
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Error loading rating history:', error);
        alert('加载历史记录失败');
    }
}

// 修改编辑评分的函数
async function editRating(character_id) {
    try {
        const userId = localStorage.getItem('userId');
        const response = await fetch(`/api/character/edit/${userId}/${character_id}`);
        
        if (!response.ok) {
            throw new Error('Failed to load character for edit');
        }
        
        currentCharacter = await response.json();
        
        // 保存rating_id用于后续更新
        localStorage.setItem('editingRatingId', currentCharacter.rating_id);
        
        // 清空selectedImages集合
        selectedImages.clear();
        
        // 设置新的选择
        if (currentCharacter.selected_images) {
            currentCharacter.selected_images.forEach(img => {
                const imageUrl = `/static/${img.type === 'face' ? 'character_images_face' : 'character_images'}/${currentCharacter.character}/${img.filename}`;
                selectedImages.add(imageUrl);
            });
        }
        
        // 显示评分界面（编辑模式）
        showRatingInterface(true);
        
    } catch (error) {
        console.error('Error loading character for edit:', error);
        alert('加载角色信息失败，请重试');
    }
}

// 修改显示评分界面的函数
function showRatingInterface(isEditing = false) {
    document.getElementById('main-container').innerHTML = `
        <h1>角色图片评分</h1>
        <div class="user-info">
            <span>当前用户: <strong id="current-user">${localStorage.getItem('userId')}</strong></span>
            <div class="user-actions">
                <button onclick="showRatingHistory()" class="secondary-button">历史记录</button>
                <button onclick="resetUser()" class="primary-button">切换用户</button>
            </div>
        </div>
        <div id="character-info"></div>
        <div id="images-container"></div>
        <div id="rating-container">
            <h3>请选择喜欢的图片</h3>
            <div class="selection-info">已选择: <span id="selected-count">${selectedImages.size}</span> 张图片</div>
            <button onclick="submitSelection()" class="primary-button">提交选择</button>
        </div>
    `;
    
    // 如果不是编辑模式，则加载新角色
    if (!isEditing) {
        // 清除编辑状态
        localStorage.removeItem('editingRatingId');
        selectedImages.clear();
        // 加载新角色
        loadCharacter();
    } else {
        // 编辑模式下直接显示当前角色
        displayCharacter();
    }
} 