import os
import instaloader

from dotenv import load_dotenv
from ExecutionAuthorizer import ExecutionAuthorizer


def get_instagram_data(username, tracked_username):
    # Create an Instaloader instance
    il = instaloader.Instaloader()

    try:
        # Login to Instagram
        il.load_session_from_file(username)
        print()
    except FileNotFoundError:
        # Request the firefox procedure because there is no session file
        print("Session file does not exist - execute the following procedure:")
        print("1) Login to Instagram in Firefox")
        print("2) Run import_firefox_session.py")
        exit(0)

    # Get the profile
    profile = instaloader.Profile.from_username(il.context, username)

    # Initialize tracked username profile
    tracked_username_profile = next((f for f in profile.get_followees() if f.username == tracked_username), None)

    # Exit if the tracked username profile wasn't found
    if tracked_username_profile is None:
        print("Tracked username ({}) NOT found".format(tracked_username))
        exit(0)

    # Create the lists
    followers_list = list(tracked_username_profile.get_followers())
    following_list = list(tracked_username_profile.get_followees())

    return followers_list, following_list


if __name__ == '__main__':

    authorizer = ExecutionAuthorizer()

    authorized, remaining_time = authorizer.authorize_execution()

    if not authorized:
        print("Not enough time has passed to execute the program.")
        print("Time remaining: {}".format(remaining_time))
        exit(0)
    else:
        print("Execution authorized.\n")

    # TODO: make EnvironmentManager (it shall ask to enter username and tracked username if env doesn't exist)
    # Load local variables from .env file
    load_dotenv()

    instagram_username = os.getenv('INSTAGRAM_USERNAME')
    instagram_tracked_username = os.getenv('INSTAGRAM_TRACKED_USERNAME')

    # TODO: make DataGrabber
    # TODO: save grabbed data in state, to track new and lost followers and following
    # Get instagram data
    followers, following = get_instagram_data(instagram_username, instagram_tracked_username)

    followers_userid_set = set(follower.userid for follower in followers)
    following_userid_set = set(followed.userid for followed in following)

    followers_friends = [follower for follower in followers if follower.userid in following_userid_set]

    followers_fans = [follower for follower in followers if follower.userid not in following_userid_set]

    following_friends = [followed for followed in following if followed.userid in followers_userid_set]
    following_no_follow_back = [followed for followed in following if followed.userid not in followers_userid_set]

    # TODO: make FileManager
    # Create followers file
    with open('followers.txt', 'w') as followers_file:
        for follower in followers:
            followers_file.write(follower.username + '\n')

    print(f"Created {followers_file.name} file.")

    # Create followers_friends file
    with open('followers_friends.txt', 'w') as followers_friends_file:
        for follower_friend in followers_friends:
            followers_friends_file.write(follower_friend.username + '\n')

    print(f"Created {followers_friends_file.name} file.")

    # Create followers_fans file
    with open('followers_fans.txt', 'w') as followers_fans_file:
        for follower_fan in followers_fans:
            followers_fans_file.write(follower_fan.username + '\n')

    print(f"Created {followers_fans_file.name} file.\n")

    # Create following file
    with open('following.txt', 'w') as following_file:
        for followed in following:
            following_file.write(followed.username + '\n')

    print(f"Created {following_file.name} file.")

    # Create following_friends file
    with open('following_friends.txt', 'w') as following_friends_file:
        for followed_friend in following_friends:
            following_friends_file.write(followed_friend.username + '\n')

    print(f"Created {following_friends_file.name} file.")

    # Create following_no_follow_back file
    with open('following_no_follow_back.txt', 'w') as following_no_follow_back_file:
        for followed_no_follow_back in following_no_follow_back:
            following_no_follow_back_file.write(followed_no_follow_back.username + '\n')

    print(f"Created {following_no_follow_back_file.name} file.\n")

    # Print results
    print("Data update complete.")
    print(f"\tFollowers: {len(followers)} "
          f"({len(followers_friends)} friends, {len(followers_fans)} fans)")
    print(f"\tFollowing: {len(following)} "
          f"({len(following_friends)} friends, {len(following_no_follow_back)} no-follow-back)")
