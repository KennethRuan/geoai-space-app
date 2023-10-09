# Databuilder

### Mapping Data for Societal Benefit

![Visuals](https://github.com/KennethRuan/geoai-space-app/blob/master/data_visualization.png)

We built a powerful compositing tool specifically designed to generate AI training datasets from meshes of publicly available data, making it the ideal aide for AI researchers and analysts. 

We strove to make the design intuitive for just about anyone to use, improving the accessibility of the data for the general population while still being capable of powering modern-day research.

An ambitious future for both civilian science as well as academic research lies ahead for DataBuilder and the OpenAI community.

### The Goal

The goal is that DataBuilder will be an intuitive resource for users to preview datasets and will act as a helpful building block for researchers. We hope the app will inspire others to play around with the vast and interesting world of geospatial data!

## Installation Instructions

Clone the repo in a directory of your choice. Afterwards, we'll navigate into the cloned repository.

```
cd geoai-space-app
```

Set up a virtual environment and then we'll install the libraries from `requirements.txt`

```
virtualenv venv --python=python3.9
./venv/Scripts/activate
```

```
pip install -r requirements.txt
```

Finally, we'll run a command to get the dashboard up and running.

```
streamlit run streamlit_app.py
```

The platform will now be hosted at `localhost:8501`, in most cases, but you can refer to the instructions in the terminal.
