# Credits to Erel Segal-Halevi
# at https://github.com/erelsgl

from itertools import chain, combinations
from time import gmtime, strftime
import logging, sys

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
fh = logging.FileHandler('FairPrim/static/party.txt')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)


def powerset(iterable: list):
    """
    By Martijn Pieters, from
    From https://stackoverflow.com/a/18035641/827927
    """
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return set(chain.from_iterable(combinations(s, r) for r in range(len(s) + 1)))


def proportional_budgeting(map_project_to_cost: dict, votes: list, limit: int, party, username) -> set:
    budgeted_projects = set()
    votes[:] = map(set, votes)  # convert every vote to a set
    money_per_voter = limit / len(votes)
    logger.info("-----------------------------")
    logger.info("חישוב הצבעות עבור פריימריז של מפלגת {}\nיוזם הפריימריז: {}\nתאריך יצירת הדוח: {}\n".format(party, username, strftime("%Y-%m-%d %H:%M:%S", gmtime())))
    logger.info("\nתקציב כולל (כמות מנדטים צפויה) = {}\nכמות המצביעים = {}\nמשקל כל הצבעה = {}\n".format(limit, len(votes), money_per_voter))
    for i in range(len(votes)):
        votes[i] = set(votes[i])
    map_project_set_to_cost = lambda ps: sum([map_project_to_cost[p] for p in ps])
    projects = map_project_to_cost.keys()
    sorted_project_sets = sorted(powerset(projects), key=map_project_set_to_cost, reverse=True)
    for ps in sorted_project_sets:
        supporting_votes = [vote for vote in votes if vote.issuperset(ps)]
        supporting_money = money_per_voter * len(supporting_votes)
        if map_project_set_to_cost(ps) <= supporting_money:
            if map_project_set_to_cost(ps) > 0:
                logger.info("{}: סך הכל הצבעות שהתקבלו {} ונבחר בהצלחה!".format(
                    "".join(sorted(ps)), len(supporting_votes)))
                budgeted_projects = budgeted_projects.union(ps)
                votes = [vote for vote in votes if not vote.issuperset(ps)]
        else:
            if map_project_set_to_cost(ps) <= limit:
                logger.info("{}: סך הכל הצבעות שהתקבלו {} -- לא מספיק קולות כדי להיבחר".format(
                    "".join(sorted(ps)), len(supporting_votes)))
    logger.info("-----------------------------")
    return sorted(budgeted_projects)


def run(map_project_to_cost, votes, limit, party, username):
    logger.setLevel(logging.INFO)

    return proportional_budgeting(map_project_to_cost, votes, limit, party, username)

# if __name__ == '__main__':
#     map_project_to_cost = {"a": 1, "b": 1, "c": 1, "d": 1}
#     votes = ["a", "c", "c", "b", "d", "a"]
#     limit = 3
#     run(map_project_to_cost, votes, limit)
