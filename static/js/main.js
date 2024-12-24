// 儲存當前選擇的聯絡人
let currentContact = null;
let chatHistory = [[],[]];
let level = [1,5];
let hp = 3;

const Contacts = [
    { id: "bot1", name: "海豚", img: "/static/海豚.png", index: 0 },
    { id: "bot2", name: "基哥", img: "/static/基哥.png", index: 1 }//,
    //{ id: "bot3", name: "二一石", img: "/static/二一石.png", index: 2 }
];


function start()
{
    // 載入聯絡人列表
    loadContacts();
    document.getElementById( "sendButton" ).addEventListener( "click", sendMessage, false );
    document.getElementById('messageInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // document.getElementById('imageUploadButton').addEventListener('click', () => {
    //     document.getElementById('imageInput').click();
    // });

    updateHp();
    // document.getElementById('imageInput').addEventListener('change', handleImageUpload);
    document.getElementById('searchInput').addEventListener('input', filterContacts);
    document.getElementById('restart').addEventListener('click', removeChatHistory);

    document.getElementById('Button1').addEventListener('click', () => {
        const textArea = document.getElementById('messageInput');
        const button = document.getElementById('Button1');
        // 將按鈕的文本設為 textarea 的值
        textArea.value = button.value;
        sendMessage();
    });

    document.getElementById('Button2').addEventListener('click', () => {
        const textArea = document.getElementById('messageInput');
        const button = document.getElementById('Button2');
    
        // 將按鈕的文本設為 textarea 的值
        textArea.value = button.value;
        sendMessage();
    });

} 

// Handle the image upload and set the image file to be sent
// let currentImage = null;
// function handleImageUpload(event) {
//     const file = event.target.files[0];
//     if (file && file.type.startsWith('image/')) {
//         currentImage = file;
//         const timestamp = new Date().toLocaleTimeString();
//         // addMessage("image",currentImage,timestamp);
//         alert(currentImage);
//         sendMessage();
        
//     } else {
//         alert("請選擇有效的圖片文件");
//     }
// }

// 載入聯絡人列表
async function loadContacts() {
    try {    
        const contactsList = document.getElementById('contactsList');
        contactsList.innerHTML = '';
        
        Contacts.forEach((contact) => {
            const contactElement = document.createElement('div');
            contactElement.className = 'contact-item';
            contactElement.innerHTML = `
                <div class="contact-img"><img src="${contact.img}" alt="${contact.name}" /></div>
                <div class="contact-info">
                    <div class="contact-name">${contact.name}</div>
                </div>
            `;
            
            contactElement.addEventListener('click', () => selectContact(contact));
            contactsList.appendChild(contactElement);
        });
        
        // 預設選擇第一個聯絡人
        if (Contacts.length > 0) {
            selectContact(Contacts[0]);
        }
    } catch (error) {
        console.error('載入聯絡人失敗:', error);
    }
}

// 選擇聯絡人
function selectContact(contact) {
    currentContact = contact;
    
    // 更新聊天標題
    const chatHeader = document.getElementById('chatHeader');
    chatHeader.innerHTML = `
        <div class="contact-img"><img src="${contact.img}" alt="${contact.name}" /></div>
        <div class="contact-info">
            <div class="contact-name">${contact.name}</div>
        </div>
    `;
    
    //加載並顯示聊天記錄
    loadChatHistory(contact.index);
    
    // 標記選中的聯絡人
    document.querySelectorAll('.contact-item').forEach(item => {
        item.classList.remove('active');
        if (item.querySelector('.contact-name').textContent === contact.name) {
            item.classList.add('active');
        }
    });
}

// 加載聊天記錄
function loadChatHistory(contactIndex) {
    const messagesContainer = document.getElementById('messagesContainer');
    messagesContainer.innerHTML = '';  // 清空當前顯示的訊息
    
    if (chatHistory[contactIndex].length === 0) {
        // 如果沒有記錄，顯示初始訊息
        const timestamp = new Date().toLocaleTimeString();
        if(contactIndex===0)
        {   
            addMessage("bot", "<遊戲開始>", timestamp);
            addMessage("bot", "你與主角決定前往二一石一探究竟，一陣陰風吹過，一隻邪惡的海豚赫然出現在二一石上，一鰭擋住了你的去路", timestamp);
            addMessage("bot", "主角: 根據我的小本本說，二一石海豚最喜歡的就是別人稱讚他了!", timestamp);
        }
        if(contactIndex===1)
        {   
            addMessage("bot", "池水清澈，微風輕拂。池邊石凳上坐著一位戴眼鏡的老年男子——基成先生，他手中拿著一台筆記型電腦，正在專注地敲著鍵盤。他抬起頭，看到玩家，露出了一絲狡黠的笑容。", timestamp);
            addMessage("bot", "想從我這裡拿到線索，可得證明你有寫程式的基本功!\n相信大數的問題對你們來說不是問題，嘿嘿", timestamp);
            addMessage("image", "../static/程式題目圖.png", timestamp);
            addMessage("bot", "填空處1該填入甚麼?", timestamp);
            addButton(1,level[contactIndex]);
        }
        if(contactIndex===2)
        {   
            addMessage("bot", "請將手放置在二一石上拍照已啟動傳送門", timestamp);
            addMessage('image', "../static/二一石.png", timestamp);
        }
    } else {
        chatHistory[contactIndex].forEach(message => {
            addMessage(message.type, message.content, message.timestamp);
        });
        addButton(1,level[contactIndex]);
    }

}

// 發送訊息
async function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    if (!message ) return;
    // 清空輸入框
    messageInput.value = '';
    const timestamp = new Date().toLocaleTimeString();
    // 添加使用者訊息到畫面
    if (message)
        addMessage('user', message, timestamp);
    
    // 使用 FormData 發送訊息和圖片
    let formData = new FormData();
    formData.append("message", message);
    formData.append("level", level[currentContact.index]);
    
    // if (currentImage) {
    //     alert(`${currentImage}`);
    //     addMessage('image', currentImage, timestamp);
    //     formData.append("image", currentImage);  // 添加圖片到 FormData
    //     currentImage = null;  // 發送後清除圖片
    // }

    if(level[currentContact.index]>=12)
    {
        alert("你已完成遊戲，請重新開始!");
        return;
    }

    try {
        const response = await fetch(`/api/chat/${currentContact.id}`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            level[currentContact.index] = data.level;
            const botResponse = data.message;
            const botTimestamp = new Date().toLocaleTimeString();

            if(data.level===4)
                level[currentContact.index] = data.level + 1;
            if(data.level === 11||data.level === 12 )
            {
                const final = data.templatemessage;
                rollDice(final,data.level);
            }

            addMessage('bot', botResponse, botTimestamp);
            addImage(data.is_pass, data.level);
            addButton(data.is_pass, data.level);
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error('發送訊息失敗:', error);
        addMessage('error', '發送訊息失敗，請稍後再試。');
    }
}

function addButton(is_pass, level){
    const botTimestamp = new Date().toLocaleTimeString();    
    let Button1 = document.getElementById("Button1");
    let Button2 = document.getElementById("Button2");
    Button1.style.display = "none";
    Button2.style.display = "none";

    if(level===5)
    {
        Button1.textContent = "sum += num1[i]-'0'";
        Button1.value = "sum += num1[i]-'0'";
        Button2.textContent = "sum += num1";
        Button2.value = "sum += num1";
        Button1.style.display = "inline-block";
        Button2.style.display = "inline-block";
    }
    if(level===6)
    {
        Button1.textContent = "(sum % 10)-'0'";
        Button1.value = "(sum % 10)-'0'";
        Button2.textContent = "(sum % 10)+'0'";
        Button2.value = "(sum % 10)+'0'"; 
        Button1.style.display = "inline-block";
        Button2.style.display = "inline-block";
    }
    if(level===9)
    {
        Button1.textContent = "上樓";
        Button1.value = "上樓吧，我覺得那腳印很可疑"; 
        Button2.textContent = "下樓";
        Button2.value = "下樓，那腳印一定是障眼法!";
        Button1.style.display = "inline-block";
        Button2.style.display = "inline-block";
    }
    
}

function addImage(is_pass, level){
    const botTimestamp = new Date().toLocaleTimeString();
    if(!is_pass)
    {
        hp=hp-1;
        updateHp();
    }

    if(!is_pass && level<4) 
        addMessage('image', "../static/海豚甩尾圖.png", botTimestamp);
    if(is_pass && level===4)
    {
        addMessage('image', "../static/二一石.png", botTimestamp);
        addMessage('bot', "請去找基哥", botTimestamp);
    }
    if(!is_pass && (level===5 || level==6))
        addMessage('image', "../static/基哥重修圖.png", botTimestamp);
    
    if(is_pass && level===7)
        addMessage('image', "../static/1201提示程式碼圖.png", botTimestamp);
    if(level===8)
    {
        addMessage('bot', "請觀察以下的校園地圖，你有沒有覺得圖上的藍點加上我們走過的地方，可以連成一個圖案，那個圖案是甚麼呢? 提示: 五角星or海豚or校長", botTimestamp);
        addMessage('image', "../static/校園地圖.jpg", botTimestamp);
    }
    if(level===9)
    {
        addMessage('bot', "追去樓梯口，現在有兩種選擇，請問你要上樓還下樓呢?", botTimestamp);
    }
}

// 添加訊息到畫面
function addMessage(type, content, timestamp) {
    const messagesContainer = document.getElementById('messagesContainer');
    const messageElement = document.createElement('div');
    messageElement.className = `message ${type}-message`;
    
    if (type === 'bot' || type === 'user') {
        messageElement.innerHTML = `
            <div class="message ${type}">
                <div class="message-content">${content}</div>
                <div class="message-timestamp">${timestamp}</div>
            </div>
        `;
    } else if (type === 'image') {
        messageElement.innerHTML = `
            <div class="message ${type}">
                <img src="${content}" alt="Image" class="message-image" onclick="showImageModal('${content}')">
                <div class="message-timestamp">${timestamp}</div>
            </div>
        `;
    }
    
    messagesContainer.appendChild(messageElement);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    updateChatHistory(type, content, timestamp);
}

// 過濾聯絡人
function filterContacts() {
    const searchText = document.getElementById('searchInput').value.toLowerCase();
    const contactItems = document.querySelectorAll('.contact-item');
    
    contactItems.forEach(item => {
        const name = item.querySelector('.contact-name').textContent.toLowerCase();
        item.style.display = name.includes(searchText) ? 'flex' : 'none';
    });
}

// 更新聊天記錄到本地存儲
function updateChatHistory(type, content, timestamp) {
    chatHistory[currentContact.index].push({
        type: type,
        content: content,
        timestamp: timestamp
    });
}

// 清空本地存儲資料
function removeChatHistory() {
    chatHistory=[ [],[]];
    level = [1,5];
    hp = 3;
    updateHp();
    const messagesContainer = document.getElementById('messagesContainer');
    messagesContainer.innerHTML = '';  // 清空當前顯示的訊息
    let Button1 = document.getElementById("Button1");
    let Button2 = document.getElementById("Button2");
    Button1.style.display = "none";
    Button2.style.display = "none";
}

function updateHp() {
    const Container = document.getElementById('hpContainer');
    Container.innerHTML = '';

    if(hp===0){
        alert("Game over!");
        removeChatHistory();
        return;
    }
    for (var i = 0; i < hp; i++) {
        const heartElement = document.createElement('img');  // 创建新的 img 元素
        heartElement.src = "../static/heart.jpg";  // 设置图片路径
        heartElement.alt = "Heart";  // 设置 alt 属性
        heartElement.classList.add('heart-image');  // 添加 class 样式
        Container.appendChild(heartElement);  // 将图片元素添加到容器
    }
}

function rollDice(finalFace, level) {
    const rollDuration = 1000; // 骰子滾動動畫持續時間（毫秒）
    const interval = 100; // 每次切換骰子圖片的時間間隔
    let elapsed = 0; // 記錄已經過的時間

    let id ="";
    if(level===11){
        id = "user-die";
    }else{
        id = "bot-die";
    }

    if(!document.getElementById(id))
    {
        const timestamp = new Date().toLocaleTimeString();
        const messagesContainer = document.getElementById('messagesContainer');
        const messageElement = document.createElement('div');
        messageElement.className = `message image-message`;
    
        messageElement.innerHTML = `
            <div class="message image">
                <img src="../static/die1.png" alt="Image" class="message-image" id=${id}>
                <div class="message-timestamp">${timestamp}</div>
            </div>
        `;

        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    let dieImages = document.getElementById(id);
    // 模擬骰子滾動的函數
    function rollAnimation() {
        // 隨機生成1到6之間的點數
        const randomFace = Math.floor(Math.random() * 6) + 1; 
        dieImages.setAttribute("src", `../static/die${randomFace}.png`); // 更新骰子圖片

        elapsed += interval; // 更新已經過的時間

        if (elapsed < rollDuration) {
            setTimeout(rollAnimation, interval); // 繼續滾動
        } else {
            dieImages.setAttribute("src", `../static/die${finalFace}.png`); 
            updateChatHistory("image", `../static/die${finalFace}.png`, timestamp);
        }
    }

    rollAnimation(); // 開始骰子滾動動畫
}

// add start
function showImageModal(imageSrc) {
    const modal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    modal.style.display = 'block';
    modalImage.src = imageSrc;
}

// 隱藏模態視窗
function hideImageModal() {
    const modal = document.getElementById('imageModal');
    modal.style.display = 'none';
}
// add end

window.addEventListener("load", start);
