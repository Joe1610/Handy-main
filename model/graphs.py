import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import seaborn as sns
# precision_recall_curve
from sklearn.metrics import precision_recall_curve, average_precision_score, roc_curve, accuracy_score
# import Model from keras
from keras.models import Model
import json
from main import load_features, build_model, LABEL_MAP_PATH
import pickle


def plot_confusion_matrix(model, X_test, y_test, label_map, indices=None):
    # Generate predictions on the test set
    y_pred = np.argmax(model.predict(X_test), axis=-1)
    y_true = np.argmax(y_test, axis=-1)

    # Filter the predictions and true labels based on the specified indices
    if indices is not None:
        y_pred = y_pred[indices]
        y_true = y_true[indices]

    # Get the relevant actions (those that are present in y_true)
    relevant_actions = []
    for i in y_true:
        if label_map[str(i)] not in relevant_actions:
            relevant_actions.append(label_map[str(i)])

    # Generate the confusion matrix and calculate percentages
    cm = confusion_matrix(y_true, y_pred, labels=list(
        range(len(relevant_actions))))
    cm_perc = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    sns.heatmap(cm_perc, annot=True, cmap="Reds",
                fmt=".1%", xticklabels=relevant_actions, yticklabels=relevant_actions)
    plt.xlabel('Predicted label')
    plt.ylabel('True label')
    plt.show()


def plot_action_accuracy(model, X_test, y_test, actions):
    # Generate predictions on the test set
    y_pred = np.argmax(model.predict(X_test), axis=-1)
    y_true = np.argmax(y_test, axis=-1)

    # Calculate the accuracy for each action
    action_acc = {}
    for i, action in enumerate(actions):
        action_indices = np.where(y_true == i)[0]
        action_acc[action] = accuracy_score(
            y_true[action_indices], y_pred[action_indices])

    action_acc_map = sorted(
        action_acc.items(), key=lambda x: x[1], reverse=True)

    # display the top 50 actions with highest accuracy
    # print only the action name

    print(action_acc_map)

    # Plot the accuracy for each action
    plt.bar(actions, action_acc.values())
    plt.title('Model Accuracy by Action')
    plt.xlabel('Action')
    plt.ylabel('Accuracy')
    plt.show()

# display the loss and accuracy of the model


def plot_loss_accuracy(history):
    # Plot the loss and accuracy of the model
    plt.plot(history['loss'], label='train')
    plt.plot(history['val_loss'], label='validation')
    plt.title('Model Loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend()
    plt.show()

    plt.plot(history['accuracy'], label='train')
    plt.plot(history['val_accuracy'], label='validation')
    plt.title('Model Accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend()
    plt.show()


def main():
    # Load the data
    batch_sizes = [20, 25, 100]
    label_map = {}
    with open(LABEL_MAP_PATH) as fp:
        label_map = json.load(fp)
    actions = np.array(list(label_map.values()))

    print("actions: ", actions)

    X_train, y_train = load_features(actions, label_map, data_type='train')
    X_test, y_test = load_features(actions, label_map, data_type='test')

    for batch in batch_sizes:
        print('batch size: ', batch)
        model = build_model(actions)
        model.load_weights(f"./models/best_model{batch}.h5")
        with open(f'history{batch}.pkl', 'rb') as file:
            history = pickle.load(file)

        plot_confusion_matrix(model, X_test, y_test, label_map)

        plot_loss_accuracy(history)
        plot_action_accuracy(model, X_test, y_test, actions)


if __name__ == '__main__':
    main()
