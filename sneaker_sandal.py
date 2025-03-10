# -*- coding: utf-8 -*-
"""ML-ProjA-2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/18QAZthO_l3bedw1OYn5RMz_78Ss5sak5
"""

import os
import numpy as np
import warnings
import pandas as pd

from scipy.stats import randint
import sklearn.neural_network
import sklearn.pipeline
import sklearn.linear_model
import sklearn.model_selection
from sklearn.metrics import accuracy_score
from sklearn.metrics import zero_one_loss
from sklearn.model_selection import cross_validate
from sklearn.model_selection import train_test_split

from sklearn.metrics import roc_auc_score

# Commented out IPython magic to ensure Python compatibility.
from matplotlib import pyplot as plt
# %matplotlib inline

import seaborn as sns
sns.set('notebook', font_scale=1.25, style='whitegrid')

"""# Data Parsing"""

DATA_DIR = './data'
SEED = 7

x_tr_MF = np.loadtxt(os.path.join(DATA_DIR, 'x_train.csv'), delimiter=',', skiprows=1)
x_te_PF = np.loadtxt(os.path.join(DATA_DIR, 'x_test.csv'), delimiter=',', skiprows=1)

y_tr_M = np.loadtxt(os.path.join(DATA_DIR, 'y_train.csv'), delimiter=',', skiprows=1)

"""# 0) Baseline: raw pixel features, fed into a Logistic Regression classifier"""

# Hyperparameter selection
C_grid = np.logspace(-9, 6, 31)

log_loss_tr_list = list()
log_loss_va_list = list()

for C in C_grid:
  lr = sklearn.linear_model.LogisticRegression(C=C, max_iter=1000, solver='lbfgs');

  scores = cross_validate(lr, x_tr_MF, y_tr_M, cv=5, scoring='neg_log_loss', return_train_score=True)

  mean_log_loss_va    = np.mean(scores['test_score'])
  mean_log_loss_tr    = np.mean(scores['train_score'])

  log_loss_tr_list.append(mean_log_loss_tr)
  log_loss_va_list.append(mean_log_loss_va)

log_loss_tr_list = np.negative(log_loss_tr_list)
log_loss_va_list = np.negative(log_loss_va_list)

plt.plot(np.log10(C_grid), log_loss_tr_list, 'b.-', label='train log loss')
plt.plot(np.log10(C_grid), log_loss_va_list, 'r.-', label='valid log loss')

plt.title('Hyperparameter Selection with Cross-Validation: Log Loss vs. log_{10} C');
plt.ylabel('log loss rate')
plt.xlabel("log_{10} C");
plt.legend(bbox_to_anchor=(1.5, 0.5)) # make legend outside plot

# best_C = C_grid[np.argmin(log_loss_va_list)]
best_C = 0.31622776601683794

lr = sklearn.linear_model.LogisticRegression(C=best_C, max_iter=1000, solver='lbfgs');

scores = cross_validate(lr, x_tr_MF, y_tr_M, cv=5, scoring='accuracy', return_train_score=True)

mean_score_va = np.mean(scores['test_score'])

print(best_C)
print(mean_score_va)
print(1 - mean_score_va)

# 0.31622776601683794
# 0.9603333333333334
# 0.03966666666666663

# Baseline Final Model with optimal hyperparameters
X_train, X_va, y_train, y_va = train_test_split(x_tr_MF, y_tr_M, test_size=0.1, random_state=SEED)

lr_1 = sklearn.linear_model.LogisticRegression(C=best_C, max_iter=1000, solver='lbfgs');

lr_1.fit(X_train, y_train)

yproba1_tr= lr_1.predict_proba(X_train)[:,1]
yproba1_va= lr_1.predict_proba(X_va)[:,1]

yhat1_tr = lr_1.predict(X_train)
yhat1_va = lr_1.predict(X_va)

plt.subplots(nrows=1, ncols=1, figsize=(5,5));

plt.title("ROC on Training/Heldout Set");
plt.xlabel('false positive rate');
plt.ylabel('true positive rate');
plt.legend(loc='lower right');
B = 0.01
plt.xlim([0 - B, 1 + B]);
plt.ylim([0 - B, 1 + B]);

lr1_tr_fpr, lr1_tr_tpr, ignore = sklearn.metrics.roc_curve(y_train, yproba1_tr)
lr1_va_fpr, lr1_va_tpr, ignore = sklearn.metrics.roc_curve(y_va, yproba1_va)


plt.plot(lr1_tr_fpr, lr1_tr_tpr, 'b.-', label="Training Set")
plt.plot(lr1_va_fpr, lr1_va_tpr, 'r.-', label="Heldout Set")


plt.legend(bbox_to_anchor=(1.55, 0.5));

print(roc_auc_score(y_train, yhat1_tr))
print(roc_auc_score(y_va, yhat1_va))

"""# 1) A feature transform of your own design, fed into a Logistic Regression classifier"""

def count_vertical_gaps(x_train):
    counts = np.empty((x_train.shape[0], 1))
    for index, x in enumerate(x_train):   # for each example
        x = np.reshape(x, (28, 28))
        count = 0
        for i in range(28):
            entered_shoe = False
            length_of_gap = 0
            for j in range(28):                    
                if x[j][i] == 0:
                    if entered_shoe:
                        length_of_gap += 1
                else:
                    entered_shoe = True
                    if length_of_gap >= 2:
                        count += 1
                        length_of_gap = 0
        counts[index] = count
    return counts

vertical_gaps_M = count_vertical_gaps(x_tr_MF)
trans_x_tr_MF = np.hstack((x_tr_MF, vertical_gaps_M))

vertical_gaps_P = count_vertical_gaps(x_te_PF)
trans_x_te_PF = np.hstack((x_te_PF, vertical_gaps_P))

# Hyperparameter selection
C_grid = np.logspace(-9, 6, 31)

log_loss_tr_list = list()
log_loss_va_list = list()

for C in C_grid:
  lr = sklearn.linear_model.LogisticRegression(C=C, max_iter=1000, solver='lbfgs');

  scores = cross_validate(lr, trans_x_tr_MF, y_tr_M, cv=5, scoring='neg_log_loss', return_train_score=True)

  mean_log_loss_va    = np.mean(scores['test_score'])
  mean_log_loss_tr    = np.mean(scores['train_score'])

  log_loss_tr_list.append(mean_log_loss_tr)
  log_loss_va_list.append(mean_log_loss_va)

log_loss_tr_list = np.negative(log_loss_tr_list)
log_loss_va_list = np.negative(log_loss_va_list)

plt.plot(np.log10(C_grid), log_loss_tr_list, 'b.-', label='train log loss')
plt.plot(np.log10(C_grid), log_loss_va_list, 'r.-', label='valid log loss')

plt.title('Hyperparameter Selection with Cross-Validation: Log Loss vs. log_{10} C');
plt.ylabel('log loss rate')
plt.xlabel("log_{10} C");
plt.legend(bbox_to_anchor=(1.5, 0.5)) # make legend outside plot

# best_C = C_grid[np.argmin(log_loss_va_list)]
best_C = 0.31622776601683794

lr = sklearn.linear_model.LogisticRegression(C=best_C, max_iter=1000, solver='lbfgs');

scores = cross_validate(lr, trans_x_tr_MF, y_tr_M, cv=5, scoring='accuracy', return_train_score=True)

mean_score_va = np.mean(scores['test_score'])

print(best_C)
print(mean_score_va)
print(1 - mean_score_va)

# 0.31622776601683794
# 0.9639166666666666
# 0.036083333333333356

# Feature Transform 1 Final Model with optimal hyperparameters

X_train, X_va, y_train, y_va = train_test_split(trans_x_tr_MF, y_tr_M, test_size=0.1, random_state=SEED)

lr_2 = sklearn.linear_model.LogisticRegression(C=best_C, max_iter=1000, solver='lbfgs');

lr_2.fit(X_train, y_train)

yproba2_tr= lr_2.predict_proba(X_train)[:,1]
yproba2_va= lr_2.predict_proba(X_va)[:,1]

yhat2_tr = lr_2.predict(X_train)
yhat2_va = lr_2.predict(X_va)

plt.subplots(nrows=1, ncols=1, figsize=(5,5));

plt.title("ROC on Training/Heldout Set");
plt.xlabel('false positive rate');
plt.ylabel('true positive rate');
plt.legend(loc='lower right');
B = 0.01
plt.xlim([0 - B, 1 + B]);
plt.ylim([0 - B, 1 + B]);

lr2_tr_fpr, lr2_tr_tpr, ignore = sklearn.metrics.roc_curve(y_train, yproba2_tr)
lr2_va_fpr, lr2_va_tpr, ignore = sklearn.metrics.roc_curve(y_va, yproba2_va)


plt.plot(lr2_tr_fpr, lr2_tr_tpr, 'b.-', label="Training Set")
plt.plot(lr2_va_fpr, lr2_va_tpr, 'r.-', label="Heldout Set")


plt.legend(bbox_to_anchor=(1.55, 0.5));

print(roc_auc_score(y_train, yhat2_tr))
print(roc_auc_score(y_va, yhat2_va))

"""# 2) Another feature transform of your own design, fed into a Logistic Regression classifier or some other classifier (e.g. KNeighborsClassifier)"""

trans_x_tr_MF = np.hstack((x_tr_MF >= 0.1, vertical_gaps_M))
trans_x_te_PF = np.hstack((x_te_PF >= 0.1, vertical_gaps_P))

mlp = sklearn.neural_network.MLPClassifier(max_iter=1000)

my_parameter_distributions_by_name = dict(
    hidden_layer_sizes=randint(2, 50),
    alpha=scipy.stats.uniform(0.0, 1.0),
    solver=['lbfgs', 'adam'],
    random_state=[101, 202, 303]
)

my_scoring_metric_name = 'neg_log_loss'

my_rand_searcher = sklearn.model_selection.RandomizedSearchCV(
    mlp,
    my_parameter_distributions_by_name,
    scoring=my_scoring_metric_name,
    cv=10,
    n_iter=12
)

my_rand_searcher.fit(trans_x_tr_MF, y_tr_M)

rsearch_results_df = pd.DataFrame(my_rand_searcher.cv_results_).copy()
print("Dataframe has shape: %s" % (str(rsearch_results_df.shape)))

print("Dataframe has columns:")
for c in rsearch_results_df.columns:
    print("-- %s" % c)

param_keys = ['param_hidden_layer_sizes', 'param_alpha', 'param_random_state', 'param_solver']

# Rearrange row order so it is easy to skim
rsearch_results_df[param_keys + ['mean_test_score', 'rank_test_score']]

# bestr_mlp = mlp.set_params(**my_rand_searcher.best_params_)
# print(bestr_mlp)

bestr_mlp = sklearn.neural_network.MLPClassifier(activation='relu', alpha=0.27451304390703546, batch_size='auto',
              beta_1=0.9, beta_2=0.999, early_stopping=False, epsilon=1e-08,
              hidden_layer_sizes=36, learning_rate='constant',
              learning_rate_init=0.001, max_fun=15000, max_iter=1000,
              momentum=0.9, n_iter_no_change=10, nesterovs_momentum=True,
              power_t=0.5, random_state=101, shuffle=True, solver='adam',
              tol=0.0001, validation_fraction=0.1, verbose=False,
              warm_start=False)

scores = cross_validate(bestr_mlp, trans_x_tr_MF, y_tr_M, cv=10, scoring='accuracy', return_train_score=True)

mean_score_va = np.mean(scores['test_score'])

print(mean_score_va)
print(1 - mean_score_va)
# bestr_mlp.fit(trans_x_tr_MF, y_tr_M)

# yhat_te_P = bestr_mlp.predict_proba(trans_x_te_PF)[:,1]

# np.savetxt("yproba1_test.txt", yhat_te_P)

# 0.9809166666666667
# 0.01908333333333334

# Feature Transform 2 Final Model with optimal hyperparameters

X_train, X_va, y_train, y_va = train_test_split(trans_x_tr_MF, y_tr_M, test_size=0.1, random_state=SEED)

lr_3 = sklearn.neural_network.MLPClassifier(activation='relu', alpha=0.27451304390703546, batch_size='auto',
              beta_1=0.9, beta_2=0.999, early_stopping=False, epsilon=1e-08,
              hidden_layer_sizes=36, learning_rate='constant',
              learning_rate_init=0.001, max_fun=15000, max_iter=1000,
              momentum=0.9, n_iter_no_change=10, nesterovs_momentum=True,
              power_t=0.5, random_state=101, shuffle=True, solver='adam',
              tol=0.0001, validation_fraction=0.1, verbose=False,
              warm_start=False)

lr_3.fit(X_train, y_train)

yproba3_tr= lr_3.predict_proba(X_train)[:,1]
yproba3_va= lr_3.predict_proba(X_va)[:,1]

yhat3_tr = lr_3.predict(X_train)
yhat3_va = lr_3.predict(X_va)

plt.subplots(nrows=1, ncols=1, figsize=(5,5));

plt.title("ROC on Training/Heldout Set");
plt.xlabel('false positive rate');
plt.ylabel('true positive rate');
plt.legend(loc='lower right');
B = 0.01
plt.xlim([0 - B, 1 + B]);
plt.ylim([0 - B, 1 + B]);

lr3_tr_fpr, lr3_tr_tpr, ignore = sklearn.metrics.roc_curve(y_train, yproba3_tr)
lr3_va_fpr, lr3_va_tpr, ignore = sklearn.metrics.roc_curve(y_va, yproba3_va)


plt.plot(lr3_tr_fpr, lr3_tr_tpr, 'b.-', label="Training Set")
plt.plot(lr3_va_fpr, lr3_va_tpr, 'r.-', label="Heldout Set")


plt.legend(bbox_to_anchor=(1.55, 0.5));

print(roc_auc_score(y_train, yhat3_tr))
print(roc_auc_score(y_va, yhat3_va))

fig, axes = plt.subplots(
        nrows=4, ncols=6,
        figsize=(15, 15))

fig.tight_layout() 

fp_index = list()
fn_index = list()

index = -1

for i, img in enumerate(X_va):
  if index >= 24:
    break
  
  if yhat3_va[i] == 1.0 and y_va[i] != yhat3_va[i]:
    cur_ax.set_title('FP')
    fp_index.append(i)
    index += 1

  elif yhat3_va[i] == 0.0 and y_va[i] != yhat3_va[i]:
    cur_ax.set_title('FN')
    fn_index.append(i)
    index += 1

  else: 
    continue
  cur_ax = axes.flatten()[index-24]
  cur_ax.imshow(np.reshape(img[:-1], (28, 28)), cmap='gray', vmin=0.0, vmax=1.0)
  cur_ax.set_xticks([])
  cur_ax.set_yticks([])
  cur_ax.set_xlabel("True: " + str(y_va[i]))
  cur_ax.set_ylabel("Pred: " + str(yhat3_va[i]))

X_train, X_va, y_train, y_va = train_test_split(x_tr_MF, y_tr_M, test_size=0.1, random_state=SEED)

# MLP  
fig, axes = plt.subplots(
        nrows=4, ncols=6,
        figsize=(11, 11))

# fig.tight_layout() 

fp_index = list()
fn_index = list()

index = 0

for i, img in enumerate(X_va):
  if index >= 24:
    break
  
  cur_ax = axes.flatten()[index-24]
  
  if yhat3_va[i] == 1.0 and y_va[i] != yhat3_va[i]:
    cur_ax.set_title('FP')
    fp_index.append(i)
    index += 1

  elif yhat3_va[i] == 0.0 and y_va[i] != yhat3_va[i]:
    cur_ax.set_title('FN')
    fn_index.append(i)
    index += 1

  else: 
    continue
  
  cur_ax.imshow(np.reshape(img, (28, 28)), cmap='gray', vmin=0.0, vmax=1.0)
  cur_ax.set_xticks([])
  cur_ax.set_yticks([])
  # cur_ax.set_xlabel("True: " + str(y_va[i]))
  # cur_ax.set_ylabel("Pred: " + str(yhat3_va[i]))

plt.subplots(nrows=1, ncols=1, figsize=(5,5));

plt.title("ROC on Training Set");
plt.xlabel('false positive rate');
plt.ylabel('true positive rate');
plt.legend(loc='lower right');
B = 0.01
plt.xlim([0.0, 0.3]);
plt.ylim([0.7, 1.0]);


plt.plot(lr1_tr_fpr, lr1_tr_tpr, 'b.-', label="Baseline Model")
plt.plot(lr2_tr_fpr, lr2_tr_tpr, 'r.-', label="LR Model")
plt.plot(lr3_tr_fpr, lr3_tr_tpr, 'g.-', label="MLP Model")


plt.legend(bbox_to_anchor=(1.65, 0.5));

plt.subplots(nrows=1, ncols=1, figsize=(5,5));

plt.title("ROC on Validation Set");
plt.xlabel('false positive rate');
plt.ylabel('true positive rate');
plt.legend(loc='lower right');
B = 0.01
plt.xlim([0.0, 0.3]);
plt.ylim([0.7, 1.0]);

plt.plot(lr1_va_fpr, lr1_va_tpr, 'b.-', label="Baseline Model")
plt.plot(lr2_va_fpr, lr2_va_tpr, 'r.-', label="LR Model")
plt.plot(lr3_va_fpr, lr3_va_tpr, 'g.-', label="MLP Model")


plt.legend(bbox_to_anchor=(1.60, 0.5));

# Baseline
X_train, X_va, y_train, y_va = train_test_split(x_tr_MF, y_tr_M, test_size=0.1, random_state=SEED)

fig, axes = plt.subplots(
        nrows=4, ncols=6,
        figsize=(11, 11))

# fig.tight_layout() 

fp_index = list()
fn_index = list()

index = 0

for i, img in enumerate(X_va):
  if index >= 24:
    break
  
  cur_ax = axes.flatten()[index-24]
  
  if yhat1_va[i] == 1.0 and y_va[i] != yhat1_va[i]:
    cur_ax.set_title('FP')
    fp_index.append(i)
    index += 1

  elif yhat1_va[i] == 0.0 and y_va[i] != yhat1_va[i]:
    cur_ax.set_title('FN')
    fn_index.append(i)
    index += 1

  else: 
    continue
  
  cur_ax.imshow(np.reshape(img, (28, 28)), cmap='gray', vmin=0.0, vmax=1.0)
  cur_ax.set_xticks([])
  cur_ax.set_yticks([])
  # cur_ax.set_xlabel("True: " + str(y_va[i]))
  # cur_ax.set_ylabel("Pred: " + str(yhat1_va[i]))

