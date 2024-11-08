from .base_model import BaseSurvivalModel
import torch
import torch.nn as nn
import numpy as np
from torch.utils.data import Dataset, DataLoader
import pandas as pd
from lifelines.utils import concordance_index


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
    def __init__(self, in_features):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_features, 64),
            nn.ReLU(),
            nn.BatchNorm1d(64),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.BatchNorm1d(32),
            nn.Dropout(0.3),
            nn.Linear(32, 1)
        )

    def forward(self, x):
        return self.net(x)


class DeepSurvModel(BaseSurvivalModel):
    def __init__(self, config=None):
        super().__init__(config)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def negative_log_likelihood(self, risk_pred, times, events):
        hazard_ratio = torch.exp(risk_pred)
        log_risk = torch.log(torch.cumsum(hazard_ratio, dim=0))
        uncensored_likelihood = risk_pred.T - log_risk
        censored_likelihood = uncensored_likelihood * events
        neg_likelihood = -torch.sum(censored_likelihood)
        return neg_likelihood

    def fit(self, X, y, fname, path, pipeline_steps=None, params_cv=None,
            params_feat_sel=None, refit=False, save_model=False,
            learning_rate=0.001, batch_size=32, n_epochs=50,
            validation_split=0.2):

        # Split data into train and validation
        from sklearn.model_selection import train_test_split
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=42,
            stratify=[yi[1] for yi in y]
        )

        # Create datasets and dataloaders
        train_dataset = SurvivalDataset(X_train, y_train)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

        # Initialize network and training components
        self.model = DeepSurvNet(in_features=X.shape[1]).to(self.device)
        optimizer = torch.optim.Adam(self.model.parameters(),
                                     lr=learning_rate,
                                     weight_decay=1e-4)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='min', factor=0.5, patience=5
        )

        # Training loop
        best_val_cindex = 0
        best_model = None
        patience = 10
        patience_counter = 0

        for epoch in range(n_epochs):
            self.model.train()
            epoch_loss = 0

            for batch_X, batch_times, batch_events in train_loader:
                batch_X = batch_X.to(self.device)
                batch_times = batch_times.to(self.device)
                batch_events = batch_events.to(self.device)

                optimizer.zero_grad()
                risk_pred = self.model(batch_X)
                loss = self.negative_log_likelihood(risk_pred, batch_times, batch_events)
                loss.backward()
                optimizer.step()

                epoch_loss += loss.item()

            # Validation
            self.model.eval()
            with torch.no_grad():
                val_risks = self.predict(X_val)
                val_cindex = concordance_index(
                    [yi[0] for yi in y_val],
                    -val_risks.flatten(),
                    [yi[1] for yi in y_val]
                )

            # Learning rate scheduling
            scheduler.step(epoch_loss)

            # Early stopping check
            if val_cindex > best_val_cindex:
                best_val_cindex = val_cindex
                best_model = self.model.state_dict().copy()
                patience_counter = 0
            else:
                patience_counter += 1

            if patience_counter >= patience:
                print(f'Early stopping at epoch {epoch + 1}')
                break

            if (epoch + 1) % 5 == 0:
                print(f'Epoch [{epoch + 1}/{n_epochs}], '
                      f'Loss: {epoch_loss / len(train_loader):.4f}, '
                      f'Val C-index: {val_cindex:.3f}')

        # Load best model
        if best_model is not None:
            self.model.load_state_dict(best_model)

        self.is_fitted = True

        if save_model:
            self.save_model(path, fname)

        # Final evaluation
        train_risks = self.predict(X)
        final_cindex = concordance_index(
            [yi[0] for yi in y],
            -train_risks.flatten(),
            [yi[1] for yi in y]
        )
        print(f"\nFinal C-index on full dataset: {final_cindex:.3f}")

    def predict(self, X):
        if not self.is_fitted:
            raise Exception("Model needs to be fitted first")

        self.model.eval()
        X_tensor = torch.FloatTensor(X.values).to(self.device)
        with torch.no_grad():
            risk_scores = self.model(X_tensor)
        return risk_scores.cpu().numpy()

    def get_feature_importance(self, X, y):
        if not self.is_fitted:
            raise Exception("Model needs to be fitted first")

        importances = []
        self.model.eval()

        X_tensor = torch.FloatTensor(X.values).requires_grad_(True).to(self.device)
        risk_scores = self.model(X_tensor)

        for i in range(X.shape[1]):
            grads = torch.autograd.grad(risk_scores.sum(), X_tensor,
                                        retain_graph=True)[0]
            importance = torch.abs(grads[:, i]).mean().item()
            importances.append(importance)

        importance_df = pd.DataFrame({
            'feature': X.columns,
            'importance': importances
        }).sort_values('importance', ascending=False)

        return importance_df