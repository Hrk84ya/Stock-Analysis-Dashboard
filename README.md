# 📈 Stock Analysis Dashboard

A user-friendly dashboard for analyzing stock market data, built with Python and Streamlit. This application allows users to visualize stock trends, view recent news, and gain insights into stock performance.

## 🚀 Features
- Interactive stock price visualizations with candlestick pattern detection
- Normalized percentage-change comparison across multiple tickers
- Display of recent news with basic sentiment analysis
- Community insights board (session-scoped)
- Customizable date range selection
- CSV export of historical data

## 📦 Prerequisites
- Python >= 3.11
- Internet access (data is fetched live from Yahoo Finance)

## 🔧 Installation

```bash
# Clone the repo
git clone <repo-url>
cd Stockz

# Install dependencies (pick one)
pip install .          # using pip with pyproject.toml
# or
uv sync               # using uv
```

## 💻 Usage

```bash
streamlit run main.py
```

## 📄 License

This project is licensed under the [MIT License](LICENSE).

## 🤝 Contributing

Contributions are welcome! If you'd like to enhance the application or fix issues, please follow these steps:
1. Fork the repository.
2. Create a new branch: `git checkout -b feature-name`.
3. Make your changes and commit them: `git commit -m 'Add new feature'`.
4. Push to the branch: `git push origin feature-name`.
5. Submit a pull request detailing your changes.

## 📬 Contact

For any questions or suggestions, feel free to reach out via the repository's issues page.
