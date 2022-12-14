from flask import Blueprint, request, jsonify, session
from app.models import User, Comment, Vote, Post
from app.db import get_db
import sys
from app.utils.auth import login_required

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/users', methods=['POST'])
def signup():
    data = request.get_json()
    db = get_db()
    try:
        newUser = User(
            username=data["username"],
            email=data["email"],
            password=data["password"]
        )
        db.add(newUser)
        db.commit()
    except:
        print(sys.exe_info()[0])
        # insert failed, so send error to front end
        db.rollback()
        return jsonify(message='Signup failed'), 500
    session.clear()
    session['user_id'] = newUser.id
    session['loggedIn'] = True
    return jsonify(id=newUser.id)


@bp.route('/users/logout', methods=['POST'])
def logout():
    # remove session variables
    session.clear()
    return '', 204


@bp.route('/users/login', methods=['POST'])
def login():
    data = request.get_json()
    db = get_db()
    try:
        user = db.query(User).filter(User.email == data['email']).one()
    except:
        print(sys.exc_info()[0])
        return jsonify(message='Incorrect credentials'), 400
    if user.verify_password(data['password']) == False:
        return jsonify(message='Incorrect credentials'), 400
    session.clear()
    session['user_id'] = user.id
    session['loggedIn'] = True

    return jsonify(id=user.id)


@bp.route('/comments', methods=['POST'])
@login_required
def comment():
    data = request.get_json()
    db = get_db()
    try:
        newComment = Comment(
            comment_text=data["comment_text"],
            post_id=data["post_id"],
            user_id=session.get('user_id')
        )
    except:
        print(sys.exc_info()[0])
        db.rollback()
        return jsonify(message='error'), 500
    db.add(newComment)
    db.commit()
    return jsonify(id=newComment.id)


@bp.route('/posts/upvote', methods=["PUT"])
@login_required
def upvote():
    data = request.get_json()
    db = get_db()
    try:
        newVote = Vote(
            post_id=data["post_id"],
            user_id=session.get("user_id")
        )
        db.add(newVote)
        db.commit()
    except:
        print(sys.exc_info()[0])
        db.rollback()
        return jsonify(message='Upvote failed'), 500
    return '', 204


@bp.route('/posts', methods=['POST'])
def post():
    data = request.get_json()
    db = get_db()
    try:
        newPost = Post(
            post_url=data['post_url'],
            user_id=session.get('user_id'),
            title=data['title']
        )
        db.add(newPost)
        db.commit()
    except:
        print(sys.exc_info()[0])
        db.rollback()
        return jsonify(message='post created failed'), 500
    return jsonify(id=newPost.id)


@bp.route('/posts/<id>', methods=['PUT'])
def editPost(id):
    data = request.get_json()
    db = get_db()
    try:
        post = db.query(Post).filter(Post.id == id).one()
        post.title = data['title']
        db.commit()
    except:
        print(sys.exc_info()[0])
        db.rollback()
        return jsonify(message='post not found'), 400
    return '', 204


@bp.route('/posts/<id>', methods=['DELETE'])
def delPost(id):
    db = get_db()
    try:
        post = db.query(Post).filter(Post.id == id).one()
        db.delete(post)
        db.commit()
    except:
        print(sys.exc_info()[0])
        db.rollback()
        return jsonify(message='post not found'), 400
    return '', 204
