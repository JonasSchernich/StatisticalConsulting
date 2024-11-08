import torch
import torch.nn as nn
import numpy as np
from torch.utils.data import Dataset, DataLoader


class SurvivalDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.FloatTensor(X.values)
        self.times = torch.FloatTensor([yi[0] for yi in y])
        self.events = torch.FloatTensor([yi[1] for yi in y])

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.times[idx], self.events[idx]


class DeepSurvNet(nn.Module):
    def __init__(self, in_features, hidden_layers):
        super().__init__()
        layers = []

        layers.append(nn.Linear(in_features, hidden_layers[0]))
        layers.append(nn.ReLU())
        layers.append(nn.BatchNorm1d(hidden_layers[0]))
        layers.append(nn.Dropout(0.3))

        for i in range(len(hidden_layers) - 1):
            layers.append(nn.Linear(hidden_layers[i], hidden_layers[i + 1]))
            layers.append(nn.ReLU())
            layers.append(nn.BatchNorm1d(hidden_layers[i + 1]))
            layers.append(nn.Dropout(0.3))

        layers.append(nn.Linear(hidden_layers[-1], 1))

        self.model = nn.Sequential(*layers)

    def forward(self, x):
        return self.model(x)


class DeepSurvModel():
    def __init__(self, hidden_layers=[64, 32], learning_rate=0.001,
                 batch_size=64, n_epochs=100):
        self.hidden_layers = hidden_layers
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.n_epochs = n_epochs
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.is_fitted = False


    def calculate_c_index(self, y_true, scores):

        times = y_true['time']
        events = y_true['status']

        concordant = 0
        total = 0

        for i in range(len(times)):
            if events[i]:
                for j in range(len(times)):
                    if times[i] < times[j]:
                        total += 1
                        if scores[i] > scores[j]:
                            concordant += 1

        return concordant / total if total > 0 else 0.0

    def negative_log_likelihood(self, risk_pred, times, events):
        hazard_ratio = torch.exp(risk_pred)
        log_risk = torch.log(torch.cumsum(hazard_ratio, dim=0))
        uncensored_likelihood = risk_pred.T - log_risk
        censored_likelihood = uncensored_likelihood * events
        neg_likelihood = -torch.sum(censored_likelihood)
        return neg_likelihood

    def fit_model(self, X, y):
        dataset = SurvivalDataset(X, y)
        dataloader = DataLoader(
            dataset,
            batch_size=self.batch_size,
            shuffle=True
        )

        self.model = DeepSurvNet(
            in_features=X.shape[1],
            hidden_layers=self.hidden_layers
        ).to(self.device)

        optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=self.learning_rate
        )

        self.model.train()
        for epoch in range(self.n_epochs):
            epoch_loss = 0
            for batch_X, batch_times, batch_events in dataloader:
                batch_X = batch_X.to(self.device)
                batch_times = batch_times.to(self.device)
                batch_events = batch_events.to(self.device)

                optimizer.zero_grad()
                risk_pred = self.model(batch_X)
                loss = self.negative_log_likelihood(risk_pred, batch_times, batch_events)
                loss.backward()
                optimizer.step()

                epoch_loss += loss.item()

            if epoch % 10 == 0:
                print(f'Epoch {epoch}: Loss = {epoch_loss / len(dataloader):.4f}')

        self.is_fitted = True

    def predict_model(self, X):
        if not self.is_fitted:
            raise Exception("Model needs to be fitted first")

        self.model.eval()
        X_tensor = torch.FloatTensor(X.values).to(self.device)
        with torch.no_grad():
            risk_scores = self.model(X_tensor)
        return risk_scores.cpu().numpy()
