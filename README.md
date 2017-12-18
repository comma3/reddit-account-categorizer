# reddit-account-categorizer
Toy model to explore the different built-in SKLearn ML methods


## 1. Introduction
When I first started learning about data science, I saw a talk where the speaker mentioned that
identifying user gender was a difficult problem. I thought that this problem would be a good starting place to explore and become comfortable with SKLearn's various built-in models.

This project is a fairly straightforward exercise in

1. Collecting data from Reddit using praw
2. Filtering and categorizing comments using regex
3. Exploring SKLearn's models and hyperparameters

## 2. Conclusions
Genders are difficult to identify based on their subreddit participation. While there are a number of heavily female subreddits (e.g., xxfitness), participation in such subreddits is low, and general use is very similar.

There are many ways in which this project could be improved:

1. The subreddit space is massive and the amount of data collected is too small to perform particularly well.
2. One feature that repeatedly seemed to appear was a heavy male bias toward "particular" interests. For example, participation in /r/gaming is not very indicative of gender, but I noticed that specific games tended to have high M:F ratios. Other examples of such particular interests were specific cars and specific sports teams. I don't believe that any of the used models were ever able to make use of this observation. Dimensional reduction may be useful in this case.
3. The accuracy of the training data are in doubt. I attempted to throw out any data that were thought to be inaccurate or inconsistent, but there are many ways in which incorrectly categorized data could have slipped through.
