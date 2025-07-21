<a id="readme-top"></a>
# routejooz-api
This repo serves as the **backend** for the [IJooz Route Optimisation Platform](https://google.com) Project


> Note: This project is part of a **polyrepo** system. While the frontend is in a separate repo, this backend can still be run standalone for solving and viewing optimized routes.

## Table of Contents 
<ol>
    <li>
        <a href="#about-the-project">About The Project</a>
        <ul>
        <li><a href="#built-with">How It Works</a></li>
        <li><a href="#built-with">Built With</a></li>
        </ul>
    </li>
    <li>
        <a href="#getting-started">Getting Started</a>
        <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
        </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
</ol>


## About the Project

### How It Works
The backend process can be broken down into 3 main parts: <br>**Preprocessing, Cost Matrix Generation, Route Optimization**

1. *Preprocessing* - Given a CSV files of vending machines' IDs and their postal codes, the backend geocodes the postal codes into latitude and longitude coordinates while ensuring the depot as the first location 
2. *Cost Matrix Generation* - First generates a NxN matrix using haversine distance between each pair and only updates


### Built With
[![FastAPI](https://img.shields.io/badge/fastapi-109989?style=for-the-badge&logo=FASTAPI&logoColor=white)](Fast-url)
[![FastAPI](https://img.shields.io/badge/Google_Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)](Google-Cloud)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
## Getting Started

### Prerequisites 
<p align="right">(<a href="#readme-top">back to top</a>)</p>


###  Running & Installation 
<p align="right">(<a href="#readme-top">back to top</a>)</p>

