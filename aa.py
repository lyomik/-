from flask import Flask, render_template, jsonify, send_file
from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier, export_text
import pandas as pd
import json
import os

app = Flask(__name__)

# Load your dataset
data_train = pd.read_csv('./datasets/Mortality_train_0.2.csv')
X_train = data_train.drop(columns=['Mortality'])
y_train = data_train['Mortality']

# Train decision tree model
clf = DecisionTreeClassifier(max_depth=2)
clf.fit(X_train, y_train)

@app.route('/')
def index():
    return render_template('index.html', json_tree=get_json_tree(clf))

@app.route('/download_json')
def download_json():
    json_tree = get_json_tree(clf)
    filename = 'decision_tree.json'
    filepath = os.path.join(app.root_path, filename)
    with open(filepath, 'w') as f:
        json.dump(json_tree, f, indent=4)
    return send_file(filepath, as_attachment=True)

def get_json_tree(classifier):
    # Export decision tree to text format
    tree_rules = export_text(classifier, feature_names=X_train.columns.tolist(), spacing=3, decimals=2, class_names=['Non-mortality', 'Mortality'])

    # Convert text representation to JSON
    json_tree = {"name": "Root"}
    node_stack = [json_tree]
    depth_stack = [0]

    lines = tree_rules.split('\n')
    for line in lines:
        if not line.strip():
            continue
        depth = line.count('|')
        parts = line.split()
        node_name = ' '.join(parts[1:])
    
        node = {"name": node_name }  # Add an extra newline after each node

        while depth <= depth_stack[-1]:
            node_stack.pop()
            depth_stack.pop()

        node_stack[-1].setdefault("children", []).append(node)
        node_stack.append(node)
        depth_stack.append(depth)

    return json_tree

if __name__ == '__main__':
    app.run(debug=True)