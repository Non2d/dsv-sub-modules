# Macro Structual Features of Rebuttals

## Abstract
This is an extension of abstract argument framework proposed by Dung, specialized for parliamentary debate, a form of turn-based impromptu competitive debate.

## Competitive Debate Rules

In parliamentary debates, two teams are randomly assigned to argue either for (Government team) or against (Opposition team) a given topic called a "motion". Each team presents their arguments and rebuttals to their opponents across multiple speaking turns called "speeches".

This model focuses on two major parliamentary debate formats: North American style and Asian style. In North American style, each team has 3 speeches (6 speeches total), while in Asian style, each team has 4 speeches (8 speeches total). In both formats, the basic speaking order alternates between Government and Opposition (Government → Opposition → Government → ...), with the final two speeches reversed to ensure fairness.

## Definition of Arguments and Rebuttals

We define the following terms for our model:

- **Round**: A complete parliamentary debate match, represented as a list of speeches
- **Speech**: A single speaking turn by one debater, represented as a list of statement transcripts
- **Speeches**: A list containing the ID of the final transcript from each speech

For example, in a 6-speech round (North American style):

```
round = [["0", "1"], ["2", "3"], ["4", "5"], ["6", "7"], ["8", "9"], ["10", "11"]]
speeches = [1, 3, 5, 7, 9, 11]
```

Here, each speech contains 2 statements (transcripts), and `speeches` tracks where each speech ends.

Finally, we define **rebuttals** as a list of tuples, where each tuple contains the ID of a rebuttal transcript and the ID of the transcript it targets.

## Point of Information (POI)

In parliamentary debates, speakers can raise **Points of Information (POIs)** during their opponents' speeches. A POI is a brief interjection where the non-speaking team asks a question or makes a challenge to the current speaker.

Key characteristics of POIs:
- **Team Reversal**: When a POI is raised, the team roles are temporarily reversed - the team that is normally listening becomes the "attacking" team for that specific ADU
- **Timing**: POIs typically occur during the middle portion of speeches (not at the beginning or end)
- **Brief Duration**: POIs are usually limited to 15-30 seconds
- **Speaker Control**: The current speaker can choose to accept or decline the POI

For our model, POI ADUs have a special property: their team affiliation is opposite to the speech they appear in. For example, if a Government speaker is giving a speech and an Opposition member raises a POI, that POI ADU belongs to the Opposition team even though it appears within a Government speech.
