# AI Stock Agent Full Project Documentation

## 1. Introduction

The AI Stock Agent is a web-based intelligent decision-support system that analyzes stock market data and produces actionable recommendations in the form of `BUY`, `SELL`, or `HOLD`. The system combines live financial data collection, feature engineering, machine learning, model evaluation, and API-driven delivery into one integrated platform.

This project was developed to demonstrate how artificial intelligence can be applied to a practical financial prediction problem. Instead of relying on hardcoded rules alone, the system learns patterns from historical stock data and uses those patterns to estimate future market movement. The final result is exposed through a backend API and presented through an interactive frontend dashboard.

The project is not an autonomous trading bot. It is an intelligent advisory platform that supports decision-making by converting historical and current market signals into a prediction and a recommendation.

## 2. Project Background

Stock prices change continuously due to market demand, company performance, investor sentiment, and global events. For many students and beginner investors, it is difficult to interpret raw market data and turn it into a clear action. This project addresses that problem by building an AI-driven stock analysis agent that can:

- collect stock market data automatically,
- engineer useful indicators from that data,
- train a machine learning model,
- predict the next likely price movement,
- recommend a decision based on the prediction.

The result is a system that demonstrates core AI concepts, software engineering practice, and real-world deployment.

## 3. Problem Statement

Manual stock analysis is time-consuming and often inconsistent. A user may know a company ticker symbol but still struggle to answer practical questions such as:

- Is the current market trend positive or negative?
- Is the next movement likely upward or downward?
- Should I buy, sell, or hold based on the available evidence?

This project solves that problem by building a goal-oriented AI agent that transforms historical stock data into a recommendation that is easier for users to understand and act on.

## 4. Main Objective

The main objective of the project is to build an intelligent stock analysis platform that predicts short-term stock price movement and recommends whether the user should `BUY`, `SELL`, or `HOLD`.

## 5. Specific Objectives

- To fetch real historical stock data from Yahoo Finance.
- To prepare and engineer features from raw market data.
- To train a machine learning model for stock price prediction.
- To classify the predicted market outcome into `BUY`, `SELL`, or `HOLD`.
- To provide a user-friendly web interface for interaction.
- To expose the prediction engine through a backend API.
- To store trained models for reuse and faster future prediction.
- To demonstrate how a goal-based AI agent can operate in a practical domain.

## 6. Scope of the Project

The scope of the system includes:

- stock data retrieval for selected ticker symbols,
- feature generation from price and volume history,
- model training for each ticker and selected time period,
- prediction of the next trading outcome,
- decision support output through `BUY`, `SELL`, or `HOLD`,
- frontend visualization of metrics and recent market trend,
- deployment of backend and frontend as separate services.

The project does not include:

- direct integration with brokerage platforms,
- execution of real buy or sell orders,
- portfolio management,
- risk-adjusted wealth optimization,
- financial guarantee or investment advice certification.

## 7. Challenges the Project Addresses

This project addresses several practical and technical challenges:

### 7.1 Data Interpretation Challenge

Raw stock market data is difficult for non-experts to interpret. The system reduces that complexity by converting price history into indicators and decisions.

### 7.2 Prediction Challenge

Stock data is noisy, time-dependent, and uncertain. The project addresses this by learning from historical examples and evaluating the trained model against a baseline.

### 7.3 Decision Challenge

A price prediction alone is not always useful to users. The project converts predictions into clear action categories: `BUY`, `SELL`, and `HOLD`.

### 7.4 Deployment Challenge

Many academic projects stop at notebook-level experiments. This system goes beyond that by exposing the model through a production-style API and a usable web dashboard.

### 7.5 Reliability Challenge

Machine learning predictions can be unstable. This project addresses reliability using:

- model evaluation metrics,
- baseline comparison,
- blend-weight safety logic,
- retraining support,
- artifact validation,
- prediction caching for faster response.

## 8. Why This Platform Was Chosen

The platform was designed as a full-stack web application because it allows the AI system to be accessible, demonstrable, and easy to evaluate.

### 8.1 Why a Web Platform

- It allows users to access the AI agent through a browser.
- It provides a clear demonstration interface for lecturers and evaluators.
- It separates the AI engine from the user interface, which improves maintainability.
- It supports future scaling, deployment, and integration.

### 8.2 Why Flask for the Backend

- Flask is lightweight and suitable for API development.
- It is easy to connect with Python machine learning libraries.
- It supports rapid prototyping and clean route-based design.

### 8.3 Why React for the Frontend

- React supports an interactive and responsive user interface.
- It allows real-time rendering of prediction results.
- It cleanly separates frontend presentation from backend logic.

### 8.4 Why Yahoo Finance via yfinance

- It provides accessible historical stock market data.
- It removes the need to manually build a financial dataset.
- It is suitable for educational prototypes and experiments.

### 8.5 Why Random Forest Models

- Random Forest handles nonlinear relationships reasonably well.
- It works effectively without heavy feature scaling.
- It is robust for small to medium structured datasets.
- It provides a practical balance between performance and implementation simplicity.

## 9. Type of AI Agent Used

This project is best classified as a `goal-based intelligent agent` with a `learning component`.

### 9.1 Why It Is a Goal-Based Agent

A goal-based agent selects actions according to whether they help achieve a defined objective. In this project, the objective is:

`Predict the likely short-term stock movement and recommend the most appropriate action among BUY, SELL, or HOLD.`

The system does not simply react to one input with one hardcoded output. Instead, it:

- gathers market information,
- processes that information,
- evaluates possible outcomes,
- chooses an action that best aligns with the system goal.

### 9.2 Why It Also Has a Learning Component

The agent improves its decision basis by training models on historical data. This means the decision logic is informed by learned patterns rather than only manually written rules.

### 9.3 Why It Is Not a Simple Reflex Agent

A simple reflex agent uses fixed condition-action rules, such as:

- if price goes up, then buy,
- if price goes down, then sell.

This project is more advanced than that because its decisions depend on model outputs, learned thresholds, classifier confirmation, and evaluation metrics.

### 9.4 Why It Is Not Fully Utility-Based

Although the system evaluates model quality and uses confidence and blending, it does not yet optimize a formal utility function such as maximum profit, minimum risk, or portfolio return. Therefore, the strongest classification is still goal-based rather than fully utility-based.

## 10. How the Project Fulfills Goal-Based Agent Criteria

The project satisfies the major criteria of a goal-based agent as follows:

### 10.1 It Has a Defined Goal

The system goal is to produce a meaningful stock decision recommendation based on data-driven prediction.

### 10.2 It Perceives the Environment

The environment is the stock market data retrieved from Yahoo Finance. The agent perceives the environment through:

- `Open`, `High`, `Low`, `Close`, and `Volume` history,
- engineered features such as `MA10`, `EMA12`, `MACD`, `RSI14`, `Return1`, `Return5`, `Volatility`, and `VolumeChange`.

### 10.3 It Maintains an Internal Representation

The internal model of the environment is represented by:

- engineered feature vectors,
- trained Random Forest regressor,
- trained Random Forest classifier,
- learned quantile thresholds,
- stored model artifacts and metrics.

### 10.4 It Evaluates Alternatives Before Acting

The system computes predicted price movement, transforms that into return thresholds, compares the outcome to learned decision boundaries, and optionally checks classifier agreement before selecting the final action.

### 10.5 It Chooses Actions That Serve the Goal

The final output is one of three actions:

- `BUY` when the predicted return indicates positive opportunity,
- `SELL` when the predicted return indicates negative movement,
- `HOLD` when the predicted movement is weak or uncertain.

### 10.6 It Adapts Through Retraining

When a model is missing or retraining is requested, the system trains again using updated market data. This supports goal achievement under changing conditions.

## 11. System Overview

The system consists of three major layers:

### 11.1 Data Layer

Responsible for retrieving and cleaning historical stock data.

### 11.2 Intelligence Layer

Responsible for feature engineering, training, prediction, threshold evaluation, and decision production.

### 11.3 Presentation Layer

Responsible for exposing the system to the user through a web API and frontend dashboard.

## 12. System Architecture

The architecture is composed of the following components:

### 12.1 Frontend

Located in the `frontend/` folder.

Responsibilities:

- receives ticker input from the user,
- calls the backend API,
- displays current price, predicted price, confidence, decision, and metrics,
- shows recent price trend.

### 12.2 Backend API

Located in `app/api.py`.

Responsibilities:

- provides routes such as `/health`, `/train`, and `/predict`,
- handles query parameters,
- coordinates prediction caching,
- controls auto-training behavior when no model exists,
- returns JSON responses to the frontend.

### 12.3 Core AI Pipeline

Located in `src/`.

Responsibilities:

- fetch stock data,
- engineer features,
- train the model,
- load saved artifacts,
- produce predictions and decisions.

### 12.4 Model Storage

Located in `models/`.

Responsibilities:

- stores `.pkl` model artifacts,
- keeps per-ticker and per-period trained models,
- preserves metrics and metadata for inference.

## 13. End-to-End Workflow

The full workflow of the system is:

1. The user enters a ticker symbol in the frontend.
2. The frontend sends a request to the backend API.
3. The backend calls the main pipeline.
4. The pipeline fetches stock data from Yahoo Finance.
5. The system engineers technical features.
6. If training is required, a model is trained and stored.
7. The latest feature row is used for prediction.
8. The system computes a predicted price and predicted return.
9. The predicted return is mapped into `BUY`, `SELL`, or `HOLD`.
10. The backend returns the result as JSON.
11. The frontend displays the result to the user.

## 14. Data Source and Data Processing

### 14.1 Data Source

The project uses Yahoo Finance through the `yfinance` Python package.

### 14.2 Data Cleaning

After downloading data, the system:

- checks that the `Close` column exists,
- normalizes multi-dimensional columns if necessary,
- removes missing values,
- raises an error if no valid rows remain.

### 14.3 Feature Engineering

The following engineered features are used:

- `MA10`, `MA20`, `MA50`
- `EMA12`, `EMA26`
- `MACD`
- `RSI14`
- `Return1`, `Return5`
- `Volatility`
- `VolumeChange`

These features help the system represent trend, momentum, volatility, and trading activity.

## 15. Machine Learning Methodology

### 15.1 Models Used

The project uses two machine learning models:

- `RandomForestRegressor` to predict the next closing price.
- `RandomForestClassifier` to support the `BUY`, `SELL`, or `HOLD` decision.

### 15.2 Target Construction

The training process creates:

- `NextClose` as the next target close price,
- `FutureReturn` as the expected return,
- `DecisionTarget` as the label for `SELL`, `HOLD`, or `BUY`.

### 15.3 Training Strategy

- Data is split chronologically rather than randomly.
- About 80% of data is used for training and 20% for testing.
- This preserves time order, which is important for stock data.

### 15.4 Evaluation Metrics

The project records:

- `MAE`
- `RMSE`
- `R²`
- baseline MAE
- quality ratio
- decision accuracy

These metrics are saved in the artifact and returned in prediction results.

## 16. Decision Logic

The system decision is not hardcoded. It is learned and computed through the following process:

1. The regressor predicts the next likely price.
2. The system converts the predicted price into a predicted return.
3. Training data is used to learn lower and upper quantile thresholds.
4. If predicted return is below the lower threshold, the result is `SELL`.
5. If predicted return is above the upper threshold, the result is `BUY`.
6. Otherwise, the result is `HOLD`.
7. If the classifier agrees with the quantile-based decision, the system records that stronger consensus.

This is one of the strongest indicators that the project behaves as a goal-based decision agent rather than a simple rule-based script.

## 17. Reliability and Safety Mechanisms

To reduce unstable outputs, the project includes several safeguards:

- baseline comparison against naive prediction,
- quality ratio calculation,
- blend-weight logic for conservative prediction,
- artifact format validation,
- period matching between model and request,
- minimum row checks before training,
- cache invalidation after retraining,
- optional automatic training if no model exists.

These features improve robustness and make the system more suitable for demonstration and deployment.

## 18. API Endpoints

The backend provides the following endpoints:

### 18.1 `GET /`

Returns API identity and available endpoints.

### 18.2 `GET /health`

Returns backend health status and whether the default model is ready.

### 18.3 `GET or POST /train`

Triggers model training for a selected ticker and period.

### 18.4 `GET /predict`

Returns a prediction result for a selected ticker and period. It may auto-train if the model is missing and auto-training is enabled.

## 19. User Interface Features

The frontend dashboard provides:

- ticker input,
- prediction trigger,
- current price display,
- predicted price display,
- model estimate display,
- final decision display,
- model status display,
- confidence display,
- validation metrics display,
- recent price trend chart,
- data provenance information.

This makes the system understandable for both technical and non-technical users.

## 20. File and Module Responsibilities

### 20.1 `app/api.py`

Handles HTTP requests, caching, route logic, and API responses.

### 20.2 `src/main.py`

Acts as the pipeline orchestrator.

### 20.3 `src/fetch.py`

Fetches and validates stock data.

### 20.4 `src/features.py`

Creates engineered technical indicators.

### 20.5 `src/train.py`

Trains the models, computes metrics, and saves artifacts.

### 20.6 `src/predict.py`

Loads artifacts and produces prediction output.

### 20.7 `src/config.py`

Stores configuration constants, feature definitions, and model path rules.

### 20.8 `frontend/src/App.jsx`

Implements the frontend dashboard and renders the returned results.

## 21. Technologies Used

The major technologies used in the project are:

- Python
- Flask
- React
- Vite
- scikit-learn
- pandas
- numpy
- yfinance
- joblib
- Render
- Vercel

## 22. Deployment Summary

The system is deployed using a split architecture:

- the backend API is hosted on Render,
- the frontend application is hosted on Vercel.

This deployment structure is appropriate because:

- Python model execution is handled on the backend service,
- the frontend can remain fast and static,
- each layer can be maintained independently.

## 23. Strengths of the Project

- Uses real market data rather than manual sample input.
- Demonstrates a full AI pipeline from data to deployment.
- Produces clear, understandable actions for users.
- Uses both regression and classification models.
- Stores reusable trained artifacts.
- Includes evaluation metrics and confidence reporting.
- Supports retraining and repeated use.
- Fits the academic concept of a goal-based intelligent agent.

## 24. Limitations of the Project

- Stock markets are highly unpredictable and influenced by external events.
- The model currently focuses on historical numerical data only.
- News sentiment, macroeconomic indicators, and company fundamentals are not yet included.
- The system predicts short-term direction, not long-term investment strategy.
- The project provides decision support, not guaranteed financial advice.
- The system does not execute trades automatically.

## 25. Future Improvements

Future versions of the project could include:

- sentiment analysis from financial news,
- support for more advanced models such as LSTM or gradient boosting,
- portfolio-level recommendation,
- risk scoring,
- multi-stock comparison,
- user authentication and saved watchlists,
- explainable AI visualizations for decision reasoning,
- live streaming market updates.

## 26. Academic Justification of the Agent Design

From an academic AI perspective, this project demonstrates that a goal-based agent must do more than react. It must:

- observe the environment,
- represent the environment internally,
- reason toward a goal,
- select an action based on expected outcome.

This project does all four. It observes stock data, transforms that data into features, applies trained models to forecast likely movement, and selects one of three actions that best matches the target goal. Because the action is chosen after prediction and evaluation, the system satisfies the practical definition of a goal-based intelligent agent.

## 27. Conclusion

The AI Stock Agent is a complete intelligent decision-support system for short-term stock analysis. It combines live data acquisition, technical feature engineering, machine learning, backend API development, frontend visualization, and deployment into one working platform.

The project successfully demonstrates:

- practical use of AI in finance,
- end-to-end machine learning workflow,
- deployment of an intelligent web application,
- implementation of a goal-based agent in a real problem domain.

For academic evaluation, the most important conclusion is that the system is not only a prediction script. It is a structured intelligent agent that senses financial data, processes it, learns from it, and chooses an action that attempts to satisfy a defined goal.

## 28. Recommended Presentation Summary

If you need a short oral summary for your lecturer, you can present the project like this:

`This project is an AI Stock Agent built as a goal-based intelligent system. It collects historical stock data from Yahoo Finance, engineers technical indicators, trains machine learning models, predicts the next likely price movement, and recommends whether the user should buy, sell, or hold. The system is goal-based because it chooses actions according to a defined objective rather than using only fixed rules. It also includes a learning component because its decisions are based on trained models. The project demonstrates a full AI workflow from data collection to deployment using Flask, React, and scikit-learn.`