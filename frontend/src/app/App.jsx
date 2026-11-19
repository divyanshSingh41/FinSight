import { createContext, useContext, useEffect, useReducer, useState } from "react";
import "./App.css";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const AppContext = createContext(null);

const initialState = {
  activePage: "Home",
  messages: [],
  theme: "bright",
};

function appReducer(state, action) {
  switch (action.type) {
    case "NAVIGATE":
      return { ...state, activePage: action.page };
    case "ADD_MESSAGE":
      return { ...state, messages: [...state.messages, action.message] };
    case "TOGGLE_THEME":
      return {
        ...state,
        theme: state.theme === "bright" ? "dark" : "bright",
      };
    case "UPDATE_MESSAGE":
      return {
        ...state,
        messages: state.messages.map((message) =>
          message.id === action.id
            ? { ...message, text: action.text }
            : message
        ),
      };
    default:
      return state;
  }
}

function AppProvider({ children }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
}

function useApp() {
  const context = useContext(AppContext);
  if (!context) throw new Error("useApp must be used inside AppProvider");
  return context;
}

const companies = [
  {
    symbol: "RELIANCE",
    name: "Reliance Industries",
    price: "₹1,463.20",
    change: "21.41%",
    tone: "positive",
  },
  {
    symbol: "TCS",
    name: "Tata Consultancy Services",
    price: "₹3,824.50",
    change: "+1.1%",
    tone: "positive",
  },
  {
    symbol: "INFY",
    name: "Infosys",
    price: "₹1,638.75",
    change: "+0.5%",
    tone: "positive",
  },
  {
    symbol: "HDFCBANK",
    name: "HDFC Bank",
    price: "₹1,716.30",
    change: "−0.3%",
    tone: "negative",
  },
];

const news = [
  "Technology shares lead today’s market movement",
  "Investors watch upcoming company earnings",
  "Markets respond to the latest economic data",
];

function Sidebar() {
  const { state, dispatch } = useApp();
  const pages = ["Home", "Analysis", "Features", "Help", "About"];

  return (
    <aside className="sidebar">
      <a className="brand" href="#" onClick={(event) => event.preventDefault()}>
        <span className="brand-mark">F</span>
        <span>FinSight</span>
      </a>

      <p className="nav-label">WORKSPACE</p>
      <nav>
        {pages.map((page) => (
          <button
            key={page}
            className={`nav-item ${state.activePage === page ? "active" : ""}`}
            onClick={() => dispatch({ type: "NAVIGATE", page })}
          >
            <span className="nav-dot" />
            {page}
          </button>
        ))}
      </nav>

      {/* <div className="sidebar-note">
        <span className="status-dot" />
        Demo workspace
      </div> */}
    </aside>
  );
}

function Header() {
  const { state, dispatch } = useApp();

  const headings = {
    Home: "Your market overview",
    Analysis: "Ask, explore, understand",
    Features: "A clearer way to explore markets",
    Help: "Your guide to FinSight",
    About: "The story behind FinSight",
  };

  return (
    <header className="topbar">
      <div>
        <p className="eyebrow">FINSIGHT · {state.activePage.toUpperCase()}</p>
        <h1>{headings[state.activePage]}</h1>
      </div>

      <div className="header-actions">
        <button
          className="theme-toggle"
          type="button"
          aria-pressed={state.theme === "dark"}
          onClick={() => dispatch({ type: "TOGGLE_THEME" })}
        >
          <span aria-hidden="true">{state.theme === "bright" ? "☾" : "☀"}</span>
        </button>

        <div className="profile">
          <span className="profile-avatar">A</span>
          <span>Hi, Ayush</span>
        </div>
      </div>
    </header>
  );
}

function HomePage() {
  return (
    <>
      <section className="welcome-card">
        <div>
          <p className="eyebrow">YOUR MARKET OVERVIEW</p>
          <h2>Make your next move with more insight.</h2>
          <p className="muted">
            Explore company snapshots, market news, and AI-powered analysis.
          </p>
        </div>
        <span className="welcome-icon">↗</span>
      </section>

      <section className="section-block">
        <div className="section-heading">
          <div>
            <p className="eyebrow">SAMPLE DATA</p>
            <h2>Company snapshots</h2>
          </div>
          <span className="small-tag">Demo</span>
        </div>

        <div className="company-grid">
          {companies.map((company) => (
            <article className="company-card" key={company.symbol}>
              <div className="company-top">
                <span className="company-icon">{company.symbol.slice(0, 1)}</span>
                <span className={`change ${company.tone}`}>{company.change}</span>
              </div>
              <p className="company-name">{company.name}</p>
              <p className="company-symbol">{company.symbol}</p>
              <strong className="company-price">{company.price}</strong>
            </article>
          ))}
        </div>
      </section>

      <section className="section-block">
        <div className="section-heading">
          <div>
            <p className="eyebrow">WHAT’S HAPPENING</p>
            <h2>Market headlines</h2>
          </div>
          <span className="small-tag">Sample news</span>
        </div>
        <div className="news-list">
          {news.map((headline, index) => (
            <article className="news-item" key={headline}>
              <span className="news-number">0{index + 1}</span>
              <p>{headline}</p>
              <span className="news-arrow">↗</span>
            </article>
          ))}
        </div>
      </section>
    </>
  );
}

function getAnalysisFilters(question) {
  const companies = [
    { ticker: "RELIANCE", pattern: /\breliance(?: industries)?\b/i },
    { ticker: "TCS", pattern: /\b(?:tcs|tata consultancy services)\b/i },
    { ticker: "INFY", pattern: /\binfosys\b/i },
    {
      ticker: "HDFCBANK",
      pattern: /\b(?:hdfc(?!\s+(?:life|amc|asset))|hdfc bank|hdfcbank)\b/i,
    },
    { ticker: "ICICIBANK", pattern: /\b(?:icici bank|icicibank)\b/i },
  ];

  const company = companies.find(({ pattern }) => pattern.test(question));
  const yearMatch = question.match(
    /\b(?:FY\s*)?(20\d{2})\s*[-–]\s*(\d{2}|20\d{2})\b/i
  );

  return {
    ticker: company?.ticker ?? null,
    fiscal_year: yearMatch
      ? `${yearMatch[1]}-${yearMatch[2].slice(-2)}`
      : null,
  };
}

function AnalysisPage() {
  const { state, dispatch } = useApp();
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [progress, setProgress] = useState("");

  // useEffect(() => {
  //   const controller = new AbortController();

  //   fetch("http://localhost:8000/api/v1/health", {
  //     signal: controller.signal,
  //   })
  //     .then((response) => {
  //       if (!response.ok) throw new Error("Health check failed");
  //       return response.json();
  //     })
  //     .then(() => setApiStatus("connected"))
  //     .catch(() => {
  //       if (!controller.signal.aborted) {
  //         setApiStatus("unavailable");
  //       }
  //     });

  //   return () => controller.abort();
  // }, []);

  async function sendMessage(event) {
    event.preventDefault();

    const question = input.trim();
    if (question.length < 5 || isTyping) return;

    const assistantId = crypto.randomUUID();

    dispatch({
      type: "ADD_MESSAGE",
      message: { role: "user", text: question },
    });

    dispatch({
      type: "ADD_MESSAGE",
      message: { id: assistantId, role: "assistant", text: "" },
    });

    setInput("");
    setIsTyping(true);
    setProgress("Starting research");

    let assistantText = "";

    function updateAssistant(text) {
      assistantText += text;
      dispatch({
        type: "UPDATE_MESSAGE",
        id: assistantId,
        text: assistantText,
      });
    }

    try {
      const response = await fetch(
        "http://localhost:8000/api/v1/analysis/stream",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "text/event-stream",
          },
          body: JSON.stringify({
            question,
            ...getAnalysisFilters(question),
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || `Request failed (${response.status})`
        );
      }

      if (!response.body) {
        throw new Error("Streaming response is not supported by this browser.");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        const frames = buffer.split(/\r?\n\r?\n/);
        buffer = frames.pop() || "";

        for (const frame of frames) {
          const dataLine = frame
            .split(/\r?\n/)
            .find((line) => line.startsWith("data:"));

          if (!dataLine) continue;

          const eventData = JSON.parse(dataLine.slice(5).trim());

          if (eventData.type === "status") {
            setProgress(eventData.stage);
          } else if (eventData.type === "token") {
            updateAssistant(eventData.text);
          } else if (eventData.type === "error") {
            throw new Error(eventData.message);
          }
        }
      }

      if (!assistantText) {
        updateAssistant("The analysis completed without returning report text.");
      }
    } catch (error) {
      console.error("Streaming analysis failed:", error);

      dispatch({
        type: "UPDATE_MESSAGE",
        id: assistantId,
        text: error.message || "The analysis failed. Please try again.",
      });
    } finally {
      setProgress("");
      setIsTyping(false);
    }
  }

  return (
    <section className="analysis-layout">
      <div className="analysis-intro">
        <p className="eyebrow">FINSIGHT ASSISTANT</p>
        <h2>What would you like to understand?</h2>
        <p className="muted">
          Ask about a company, market concept, or financial question.
        </p>
        {/* <p className="muted">
          API status:{" "}
          {apiStatus === "checking"
            ? "checking…"
            : apiStatus === "connected"
              ? "connected"
              : "unavailable"}
        </p> */}
      </div>

      <div className="chat-panel">
        <div className="chat-messages">
          {state.messages.length === 0 ? (
            <div className="empty-chat">
              <span className="chat-spark">✳</span>
              <h3>Start a conversation</h3>
              <p>Ask a question to get a FinSight analysis.</p>
            </div>
          ) : (
            state.messages.map((message, index) => (
              <div className={`message ${message.role}`} key={index}>
                <span className="message-avatar">
                  {message.role === "user" ? "A" : "F"}
                </span>
                {message.role === "assistant" ? (
                  <div className="message-content">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {message.text || ""}
                    </ReactMarkdown>
                  </div>
                ) : (
                  <p>{message.text}</p>
                )}
              </div>
            ))
          )}

          {isTyping && (
            <p className="typing-indicator">
              {progress || "FinSight is researching…"}
            </p>
          )}
        </div>

        <form className="chat-form" onSubmit={sendMessage}>
          <input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Ask FinSight a question..."
            aria-label="Message FinSight"
          />
          <button
            type="submit"
            disabled={input.trim().length < 5 || isTyping}
            aria-label="Send message"
          >
            ↑
          </button>
        </form>

        <p className="chat-disclaimer">
          Analysis generated by the FinSight backend.
        </p>
      </div>
    </section>
  );
}

const pageContent = {
  Features: {
    eyebrow: "WHAT FINSIGHT CAN DO",
    title: "Tools for clearer financial research.",
    items: [
      ["Company insights", "Review company information and key analysis in one place."],
      ["Market news", "Browse news summaries alongside your research workflow."],
      ["AI analysis chat", "Ask questions in a conversational interface."],
      ["Focused workspace", "Move between your overview, analysis, and guidance."],
    ],
  },
  Help: {
    eyebrow: "GETTING STARTED",
    title: "How to use FinSight.",
    items: [
      ["01 · Home", "Browse the sample company snapshots and market headlines."],
      ["02 · Analysis", "Type a question in the chat box and press the arrow or Enter."],
      ["03 · Features", "Review the tools available in this workspace."],
      ["04 · About", "Learn who created FinSight and why."],
    ],
  },
};

function InfoPage({ page }) {
  const content = pageContent[page];

  return (
    <section className="section-block">
      <div className="section-heading">
        <div>
          <p className="eyebrow">{content.eyebrow}</p>
          <h2>{content.title}</h2>
        </div>
      </div>
      <div className="info-grid">
        {content.items.map(([title, description]) => (
          <article className="info-card" key={title}>
            <span className="info-mark">✳</span>
            <h3>{title}</h3>
            <p className="muted">{description}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function AboutPage() {
  const developers = [
    {
      initials: "AS",
      name: "Ayush Solanki",
      role: "Full Stack Developer",
      extra: "Coordination Support",
      number: "01",
    },
    {
      initials: "DP",
      name: "Divyansh Pratap Singh",
      role: "AI/ML Developer",
      extra: "",
      number: "02",
    },
    {
      initials: "AK",
      name: "Ashwani Kumar",
      role: "Backend Developer",
      extra: "",
      number: "03",
    },
    {
      initials: "DG",
      name: "Dev Gupta",
      role: "Team Member",
      extra: "Research & Presentation",
      number: "04",
    },
  ];

  return (
    <section className="about-page">
      <div className="about-hero">
        <div className="about-hero-copy">
          <p className="eyebrow">THE TEAM BEHIND FINSIGHT</p>
          <h2>People turning financial data into clearer decisions.</h2>
          <p>
            FinSight brings company insights, market news, and AI-powered
            analysis into one focused experience.
          </p>
        </div>
        <div className="about-hero-art" aria-hidden="true">
          <span className="orbit orbit-one" />
          <span className="orbit orbit-two" />
          <span className="orbit-core">F</span>
        </div>
      </div>

      <div className="team-heading">
        <div>
          <p className="eyebrow">MEET THE DEVELOPERS</p>
          <h3>Built by a focused team</h3>
        </div>
        <span className="team-count">{developers.length} developers</span>
      </div>

      <div className="developer-grid">
        {developers.map((developer) => (
          <article className="developer-card" key={developer.name}>
            <div className="developer-card-top">
              <span className="developer-number">{developer.number}</span>
              <span className="developer-spark" aria-hidden="true">✳</span>
            </div>

            <div className="developer-avatar">{developer.initials}</div>

            <div className="developer-info">
              <h3>{developer.name}</h3>
              <p className="developer-role">{developer.role}</p>
              {developer.extra && (
                <span className="developer-extra">{developer.extra}</span>
              )}
            </div>

            <div className="developer-card-bottom">
              <span>FINSIGHT TEAM</span>
              <span aria-hidden="true">↗</span>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function MainContent() {
  const { state } = useApp();

  return (
    <main className="main-area">
      <Header />
      <div className="page-content">
        {state.activePage === "Home" && <HomePage />}
        {state.activePage === "Analysis" && <AnalysisPage />}
        {["Features", "Help"].includes(state.activePage) && (
          <InfoPage page={state.activePage} />
        )}
        {state.activePage === "About" && <AboutPage />}
      </div>
    </main>
  );
}

function AppLayout() {
  const { state } = useApp();

  return (
    <div className={`app-shell theme-${state.theme}`}>
      <Sidebar />
      <MainContent />
    </div>
  );
}

export default function App() {
  return (
    <AppProvider>
      <AppLayout />
    </AppProvider>
  );
}