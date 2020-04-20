# Finding the best location for our company
## *Geocoding project*
![image](/INPUT/readmeimage.jpg)


## 1. Objective
Find the best location to settle down our company using geocoding libraries and techniques.


## 2. Requirements
The company has several needs that we have to fulfill:
1. An airport closeby so that the account managers can travel.
2. Near to a Starbucks to have some coffee in the morning.
3. Far from companies with more than 10 years.
4. Next to a vegan restaurant.
5. Next to schools so employees can leave their children.
6. Near to a pub to hanggle out with the colleagues.
7. Near an auditorium or place where talks and conferences are given.
  

## 3. Procedure
To face this problem, we will divide it in two parts.

#### Part 1
With plotly library we will plot worldwide data to have a better overview of the European candidate cities to host our company. We'll decide one of them and we'll plot the available area that meets our first three requirements.

#### Part 2
Having decided the city, we'll use the Foursquare API to find the rest of points of interest, which will be visualized with cartoframes. Again, we will filter a smaller area and we'll calculate the space available for our company. The best location is plotted with folium.
