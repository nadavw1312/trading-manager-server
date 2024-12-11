import git

def commit_calculations_doc():
    # Path to your local repository
    repo_path = '/Users/calculation'

    # Initialize the repository
    repo = git.Repo(repo_path)

    # Add the file to the staging area
    repo.index.add(['calculations_doc.txt'])

    # Commit the changes
    repo.index.commit('Add generated calculations_doc')

    # Push the changes to the remote repository
    origin = repo.remote(name='origin')
    origin.push()