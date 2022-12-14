# octo-plus
## Formula extractor tool
---
### Hackathon (Summer Edition) 2022

In this project, we solve the task of finding formula between dependent variables via polynomial regression (degree = 3), where the significant coefficients are given via Lasso regression.

To run the web-server, clone the repo and run the following:
```
python3 app.py
```

The web app will show up at http://127.0.0.1:5500/

To see the code for polynomial regression, go to folder 'notebooks', then to notebook 'polynomial.ipynb'.

To see the code for Lasso regression, go to 'master' branch, then to notebook 'polynomial.ipynb'.

Example code for the most important coefficients:

```
from sklearn.linear_model import LassoCV, Lasso, LinearRegression, RidgeCV, Ridge
from joblib import parallel_backend

y = df['fee']
X = df[['base','rate', 'days_diff']] 

pol = PolynomialFeatures(degree=3)
X_pol = pol.fit_transform(X)
lasso1 = Lasso(alpha=lassocv1.alpha_, normalize=True)
lasso1.fit(X_pol, y)
coeffs1 = lasso1.coef_

index_list=[]
for i in range(len(lasso1.coef_)):
    if abs(lasso1.coef_[i])!=0:
        index_list.append(i)
        
print(index_list)
print(coeffs1)
```
