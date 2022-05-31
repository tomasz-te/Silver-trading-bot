## Silver trading bot

The aim of this project is to build a silver trading strategy using ensemble models. Then, using the best machine learning model, we will try to build a dashboard for our strategy and implement it in real life on Interactive Brokers.

The model-based strategy has a higher Sharpe ratio, which means it delivers better risk-adjusted returns. Therefore model can be used in practice when building an investment portfolio.

The weak point of the strategy is that it is very sensitive to when it starts beeing aplied. The solution to this problem may be to divide the capital into N equal parts and execute the strategy every 10/N day.

Run signal generator here: https://slv-bot.herokuapp.com/
