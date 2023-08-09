import { useState } from "react";
import "./App.css";
import "@chatscope/chat-ui-kit-styles/dist/default/styles.min.css";
import {
  MainContainer,
  ChatContainer,
  MessageList,
  Message,
  MessageInput,
  TypingIndicator,
} from "@chatscope/chat-ui-kit-react";

const API_BASE_URL = "http://127.0.0.1:8000"; // Replace with your Fast API backend URL

const systemMessage = {
  role: "system",
  content:
    "Explain things like you're talking to a software professional with 2 years of experience.",
};

function App() {
  const [messages, setMessages] = useState([
    {
      message: "Hello, I'm FastBot! Ask me anything!",
      sentTime: "just now",
      sender: "ChatGPT",
    },
  ]);
  const [isTyping, setIsTyping] = useState(false);

  const handleSend = async (message) => {
    const newMessage = {
      message,
      direction: "outgoing",
      sender: "user",
    };

    const newMessages = [...messages, newMessage];

    setMessages(newMessages);

    setIsTyping(true);
    await processMessageToChatGPT(newMessages);
  };

  async function processMessageToChatGPT(chatMessages) {
    let apiMessages = chatMessages.map((messageObject) => {
      let role = "";
      if (messageObject.sender === "ChatGPT") {
        role = "assistant";
      } else {
        role = "user";
      }
      return { role: role, content: messageObject.message };
    });

    const apiRequestBody = {
      model: "gpt-3.5-turbo",
      messages: [
        systemMessage,
        ...apiMessages,
      ],
    };

    const response = await fetch(`${API_BASE_URL}/chatbot/?user_query=${apiMessages[apiMessages.length - 1].content}`);

    try {
      // const response = await fetch(`${API_BASE_URL}/chatbot/?user_query=${apiMessages[apiMessages.length - 1].content}`);
      const response = await fetch(`${API_BASE_URL}/chatbot/?user_query=${apiMessages[apiMessages.length - 1].content}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        // body: JSON.stringify({ user_query: apiMessages[apiMessages.length - 1].content }),  Send only the latest user message for processing
      });

      const data = await response.json();

      setMessages([
        ...chatMessages,
        {
          message: data.response,
          sender: "ChatGPT",
        },
      ]);
      setIsTyping(false);
    } catch (error) {
      console.error("Error processing message:", error);
      setIsTyping(false);
    }
  }

  return (
    <div className="App">
      <div style={{ position: "relative", height: "800px", width: "700px" }}>
        <MainContainer>
          <ChatContainer>
            <MessageList
              scrollBehavior="smooth"
              typingIndicator={
                isTyping ? (
                  <TypingIndicator content="FastBot is typing" />
                ) : null
              }
            >
              {messages.map((message, i) => (
                <Message key={i} model={message} />
              ))}
            </MessageList>
            <MessageInput
              placeholder="Type message here"
              onSend={handleSend}
            />
          </ChatContainer>
        </MainContainer>
      </div>
    </div>
  );
}

export default App;