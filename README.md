# 📱 Mobile Risk Copilot

A mobile-optimized portfolio risk analysis application built with Streamlit. This is a proof-of-concept to test mobile demand before building a native iOS/Android app.

## 🚀 Features

- **Portfolio Analysis**: Real-time risk metrics (VaR, CVaR, Sharpe Ratio)
- **AI Co-pilot**: Natural language queries about your portfolio
- **Hedging Analysis**: Smart hedge recommendations based on correlations
- **Stress Testing**: See how your portfolio performs in crisis scenarios
- **Mobile-First Design**: Optimized UI/UX for mobile devices

## 🏗️ Architecture

```
Mobile App (Streamlit) → Backend APIs (FastAPI on Render) → FMP Data
```

- **Frontend**: Streamlit (mobile-optimized)
- **Backend**: Shared with desktop app (hosted on Render)
- **Data**: Financial Modeling Prep (FMP) API

## 📦 Installation

### Prerequisites
- Python 3.9+
- Backend API running (see [risk-analysis-backend](https://github.com/YOUR_USERNAME/risk-analysis-backend))

### Local Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/mobile-risk-copilot.git
cd mobile-risk-copilot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API_BASE_URL

# Run the app
streamlit run Home.py
```

The app will be available at `http://localhost:8501`

## ☁️ Deployment (Streamlit Cloud)

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app" and select this repo
4. Set main file: `Home.py`
5. Add secrets in dashboard:
   ```toml
   API_BASE_URL = "https://your-backend.onrender.com"
   ```
6. Deploy!

## 📁 Project Structure

```
mobile-risk-copilot/
├── Home.py                    # Main entry point
├── pages/
│   ├── 1_Copilot.py          # AI assistant page
│   ├── 2_Portfolio.py         # Portfolio overview
│   ├── 3_Risk.py              # Risk analysis
│   └── 4_Hedging.py           # Hedging recommendations
├── utils/
│   ├── api_client.py          # Backend API wrapper
│   ├── insights_generator.py # AI insights
│   └── portfolio_manager.py   # Portfolio state management
├── requirements.txt
├── .env.example
└── README.md
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `API_BASE_URL` | Backend API endpoint | Yes |
| `DEBUG_MODE` | Enable debug logging | No |

### Streamlit Config

Create `.streamlit/config.toml` for custom theming:

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
```

## 🛠️ Development

### Running Locally

```bash
streamlit run Home.py --server.port 8502
```

### Testing with Backend

Ensure your backend is running:
```bash
# Backend should be accessible at API_BASE_URL
curl https://your-backend.onrender.com/health
```

## 📊 Roadmap

See [IMPROVEMENTS.md](IMPROVEMENTS.md) for detailed roadmap.

**Quick Wins (Sprint 1):**
- [ ] Frontend caching
- [ ] Loading skeletons
- [ ] Real portfolio values
- [ ] Error recovery

**Upcoming Features:**
- [ ] Portfolio editing
- [ ] Historical performance charts
- [ ] Authentication system
- [ ] Push notifications (requires native app)

## 🤝 Contributing

This is a proof-of-concept for mobile demand testing. Contributions welcome!

## 📄 License

MIT License - See LICENSE file for details

## 🔗 Related Projects

- [Desktop App](https://github.com/YOUR_USERNAME/risk-analysis-backend) - Full-featured desktop version
- [Backend API](https://github.com/YOUR_USERNAME/risk-analysis-backend) - Shared FastAPI backend

## 📞 Support

Questions? Open an issue or contact via [your contact method]

---

**Built with ❤️ using Streamlit**