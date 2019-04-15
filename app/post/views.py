from flask import Blueprint, request, redirect
from flask_jwt_extended import jwt_required, jwt_optional, create_access_token, get_jwt_identity
from flask import jsonify, json, render_template, flash, redirect, request
from marshmallow import ValidationError

from app.extensions import db, login_manager, bcrypt
from .forms import SubjectCreation, TopicCreation, PostCreation
from .models import Subject, Topic, Post, Report, UpvotePost
from app.user.models import User
from .schema import SubjectSchema, subject_schema, subjects_schema
from .schema import TopicSchema, topic_schema, topics_schema
from .schema import PostSchema, post_schema, posts_schema
from .schema import ReportSchema, report_schema, reports_schema
from .schema import UpvotePostSchema, upvote_schema, upvotes_schema

postblueprint = Blueprint('post', __name__)

### SUBJECT
@postblueprint.route('/v1/subject/createSubject', methods=['POST',])
@jwt_required
def _subjectcreate():
    
    json_data = request.get_json()

    try:
        subject_data = subject_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 422

    # check for subject already created
    duplicatesubject = Subject.query.filter_by(subject=json_data['subject'].lower()).first()
    if duplicatesubject:
        return jsonify({"message": "Duplicate subject"}), 400

    # Check to see if subject exists
    current_user = get_jwt_identity()
    if current_user is not None:
        user = User.query.filter_by(username=current_user).first()
        subject = Subject(
            subject=json_data['subject'].lower(),
            description=json_data['description'].lower(),
            author_id=user.id
        )
        db.session.add(subject)
        db.session.commit()
        return jsonify(message=True,
                       id=subject.id,
                       name=subject.subject), 200
    
    return jsonify({"message": "Fail"}), 400

@postblueprint.route('/v1/subject/getAll', methods=['GET'])
def _getsubjectall():
    subjects = Subject.query.all()
    result = subjects_schema.dump(subjects, many=True)
    return jsonify({'subjects': result})

@postblueprint.route('/v1/subject/search/<subjectstr>', methods=['GET'])
def _getsubject(subjectstr):
    getsubject = Subject.query.filter_by(subject=subjectstr.lower()).first()

    if getsubject:
        return jsonify(subject_id=getsubject.id, 
                       subject_name=getsubject.subject, 
                       subject_description=getsubject.description, 
                       success='True', code=200)
    else:
        return jsonify({"message": "Subject does not found"}), 400


### TOPIC
@postblueprint.route('/v1/topic/createTopic/<int:subjectid>/', methods=['POST',])
@jwt_required
def _posttopic(subjectid):
    json_data = request.get_json()

    try:
        topic_data = topic_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 422

    # check for post already created
    duplicatetopic = Topic.query.filter_by(topic=json_data['topic'].lower()).first()
    if duplicatetopic:
        return jsonify({"message": "Duplicate post"}), 400

    # is this a valid subject
    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        topic = Topic(
            topic=json_data['topic'].lower(),
            description=json_data['description'].lower(),
            author_id=user.id,
            subject_id=subjectid
        )
        db.session.add(topic)
        db.session.commit()
        return jsonify(message=True,
                       id=topic.id,
                       name=topic.topic), 200

    return jsonify({"message": "Fail"}), 400

@postblueprint.route('/v1/topic/getTopics/<int:subjectid>/', methods=['GET',])
def _gettopicall(subjectid):

    topics = Topic.query.filter_by(subject_id=subjectid).all()
    result = topics_schema.dump(topics, many=True)
    return jsonify({'topics': result})

### POST
@postblueprint.route('/v1/post/createPost/<int:topicid>/', methods=['POST',])
@jwt_required
def _postcreate(topicid):

    json_data = request.get_json()

    try:
        post_data = post_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 422

    # check for post already created
    duplicatepost = Post.query.filter_by(resource=json_data['resource'].lower()).first()
    if duplicatepost:
        return jsonify({"message": "Duplicate post"}), 400


    #is this a valid resource
    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        post = Post(
            resource=json_data['resource'].lower(),
            resource_url=json_data['resource_url'].lower(),
            description=json_data['description'].lower(),
            author_id=user.id,
            topic_id=topicid,
        )
        db.session.add(post)
        db.session.commit()
        return jsonify(message=True,
                       id=post.id), 200

    return jsonify({"message": "Fail"}), 400


@postblueprint.route('/v1/post/getTopic/<int:topicid>/', methods=['GET',])
def _getpostalltopic(topicid):
    posts = Post.query.filter_by(topic_id=topicid).all()
    result = posts_schema.dump(posts, many=True)
    return jsonify({'posts': result})


# TODO: Add a route that returns all topics for a given subject
# @blueprint.route('/subject/<int:subjectid>/post/', methods=['GET',])
# def _getpostalltopic(subjectid):
#     posts = Post.query.filter_by(topic_id=subjectid).all()
#     result = posts_schema.dump(posts, many=True)
#     return jsonify({'posts': result})


@postblueprint.route('/v1/post/getAll', methods=['GET',])
def _getpostall():
    posts = Post.query.all()
    posts_result = posts_schema.dump(posts, many=True)
    return jsonify({'posts': posts_result})


### REPORTS

@postblueprint.route('/v1/report/createReport/<int:postid>/', methods=['POST',])
@jwt_optional
def _createreport(postid):
    json_data = request.get_json()

    try:
        report_data = report_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 422

    #is this a valid subject
    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        report = Report(
            description=json_data['description'].lower(),
            reported_post_id=postid,
            author_id=user.id,
        )
        db.session.add(report)
        db.session.commit()
        return jsonify({"message": "Success"}), 200
    else:
        user = User.query.filter_by(username=current_user).first()
        report = Report(
            description=json_data['description'].lower(),
            reported_post_id=postid,
        )
        db.session.add(report)
        db.session.commit()
        return jsonify({"message": "Success"}), 200

    return jsonify({"message": "Fail"}), 400

@postblueprint.route('/v1/report/getPostReport/<int:postid>/', methods=['GET',])
def _getpostreports(postid):
    reports = Report.query.filter_by(reported_post_id=postid).all()
    result = reports_schema.dump(reports, many=True)
    return jsonify({'reports': result})

@postblueprint.route('/v1/report/getReports', methods=['GET',])
def _getreportsall():
    reports = Report.query.all()
    result = reports_schema.dump(reports, many=True)
    return jsonify({'reports': result})

## UPVOTE POST
@postblueprint.route('/v1/vote/onPost/<int:postid>/', methods=['POST',])
@jwt_required
def _createvote(postid):
    json_data = request.get_json()

    try:
        upvote_data = upvote_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 422

    #is this a valid subject
    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(username=current_user).first()
        upvote = UpvotePost(
            vote_choice=json_data['vote_choice'],
            post_id=postid,
            user_id= user.id,
        )
        db.session.add(upvote)
        db.session.commit()
        return jsonify({"message": "Success"}), 200

    return jsonify({"message": "Fail"}), 400

@postblueprint.route('/v1/<int:postid>/vote/', methods=['GET',])
def _getpostvotes(postid):
    votes = UpvotePost.query.filter_by(post_id=postid).all()
    result = upvotes_schema.dump(votes, many=True)
    return jsonify({'reports': result})

# We will want to only allow users with the role of admin for this
@postblueprint.route('/v1/vote/getAllVotes', methods=['GET',])
@jwt_required
def _getvotesall():
    votes = UpvotePost.query.all()
    result = upvotes_schema.dump(votes, many=True)
    return jsonify({'votes': result})