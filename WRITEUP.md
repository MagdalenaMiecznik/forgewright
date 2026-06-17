# Write-Up

## Approach

How did you approach the problem? What methods did you choose and why?

At first I read the documentation and prepared the file called notes.txt to keep there the most important infromation from README, to solve the problem.


## Data exploration

What did you find when you looked at the data? How did it shape your approach?

When I loaded the data:
1. I checked the general content. 
2. How do they relate to one another. 
3. Unified date time formating.
4. I merged dataframes one by one and filterout unnecessery records (those that didn't match the other table date time range), to prevent the dataframe form exploding.
5. I grouped filtered data frame by: machine_id, job_id, part_type, start_time and end_time. The data were consistent and created 7 subgroups.
6. I looked individually at each subgroup -> job and this time focused on power vs. vibration dependecies by plotting pairplot (correlations).
7. I found out there were some values to filterout in the firs job data == 9999, probably resulting from missing values imputation.
8. From the plots shape I decided to focused on power consumption outliers and use it as a metric/ indicator of the problem.


## Validation

I analysed the plots and final df.

## Tool-wear findings

Which jobs show signs of tool wear? How confident are you?

i am quite confident about this job. It has outstanding mean power, max peak vibration and outliers number in power.

| Job | Mean power (kW) | Peak vibration (g) | Wear score | Flagged? |
|-----|-----------------|--------------------|------------|----------|
|JOB-046|14.78          | 4.2640             | 4060       |   Yes    |

## What I'd do differently

With more time or more data, what would you change?
If I have more time I would spend it on finding clear dependencies between power consumption and vibration and use it as a metric.