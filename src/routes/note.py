from flask import Blueprint, jsonify, request
from src.models.note import Note, db
from src.llm import translate_text

note_bp = Blueprint('note', __name__)

import datetime
import os
import json as _json

@note_bp.route('/notes', methods=['GET'])
def get_notes():
    """Get all notes, ordered by most recently updated"""
    # order by position if set (NULLs last), then by updated_at desc
    notes = Note.query.order_by(Note.position.asc().nullslast(), Note.updated_at.desc()).all()
    return jsonify([note.to_dict() for note in notes])

@note_bp.route('/notes', methods=['POST'])
def create_note():
    """Create a new note"""
    try:
        data = request.json
        # Log incoming create payload for debugging
        print(f"[notes:create] {datetime.datetime.utcnow().isoformat()} - incoming POST data: {data}")
        if not data or 'title' not in data or 'content' not in data:
            return jsonify({'error': 'Title and content are required'}), 400

        tags = data.get('tags', [])
        # ensure tags is a list
        if tags is None:
            tags = []

        note = Note(
            title=data['title'],
            content=data['content'],
            tags=tags,
            event_date=data.get('event_date'),
            event_time=data.get('event_time')
        )
        db.session.add(note)
        db.session.commit()
        return jsonify(note.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@note_bp.route('/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    """Get a specific note by ID"""
    note = Note.query.get_or_404(note_id)
    return jsonify(note.to_dict())

@note_bp.route('/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """Update a specific note"""
    try:
        note = Note.query.get_or_404(note_id)
        data = request.json
        print(f"[notes:update] {datetime.datetime.utcnow().isoformat()} - updating id={note_id} with data: {request.json}")
        data = request.json

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        note.title = data.get('title', note.title)
        note.content = data.get('content', note.content)
        # handle tags/event_date/event_time
        tags = data.get('tags')
        if tags is not None:
            # expect tags to be a list; assign directly so SQLAlchemy can map to JSON
            note.tags = tags

        if 'event_date' in data:
            note.event_date = data.get('event_date')

        if 'event_time' in data:
            note.event_time = data.get('event_time')
        db.session.commit()
        return jsonify(note.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@note_bp.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Delete a specific note"""
    try:
        note = Note.query.get_or_404(note_id)
        print(f"[notes:delete] {datetime.datetime.utcnow().isoformat()} - deleting id={note_id}")
        db.session.delete(note)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@note_bp.route('/notes/search', methods=['GET'])
def search_notes():
    """Search notes by title or content"""
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    notes = Note.query.filter(
        (Note.title.contains(query)) | (Note.content.contains(query))
    ).order_by(Note.updated_at.desc()).all()
    
    return jsonify([note.to_dict() for note in notes])


@note_bp.route('/notes/reorder', methods=['POST'])
def reorder_notes():
    """Reorder notes. Expects JSON body: {'order': [id1, id2, ...]}"""
    try:
        data = request.json
        order = data.get('order') if data else None
        if not order or not isinstance(order, list):
            return jsonify({'error': 'Order must be a list of note ids'}), 400

        # Update positions
        for idx, nid in enumerate(order):
            note = Note.query.get(nid)
            if note:
                note.position = idx
        db.session.commit()
        return jsonify({'status': 'ok'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@note_bp.route('/notes/translate', methods=['POST'])
def translate_free_text():
    """Translate arbitrary text provided in the request body.

    Request JSON: { content: "...", target_lang: "zh" }
    """
    try:
        data = request.json
        if not data or 'target_lang' not in data or 'content' not in data:
            return jsonify({'error': 'content and target_lang are required'}), 400

        target = data['target_lang']
        content = data['content']

        try:
            translated = translate_text(content or '', target)
        except RuntimeError as re:
            msg = str(re)
            return jsonify({
                'error': 'OpenAI call failed: No API key configured',
                'detail': msg,
                'suggestions': [
                    'Set OPENAI_API_KEY in the environment or create a .env file with OPENAI_API_KEY=sk-...',
                    'For quick local testing without a key, set MOCK_TRANSLATION=1 in your environment (development only).',
                    'If you intended to call GitHub-hosted models, set GITHUB_TOKEN and optionally BASE_URL.'
                ]
            }), 500
        except Exception as e:
            import traceback
            traceback.print_exc()
            msg = str(e)
            low = msg.lower()
            if 'timeout' in low or 'timed out' in low or 'connect' in low:
                example_curl = {
                    'ipv4': "curl --ipv4 -v https://api.openai.com/v1/models -H \"Authorization: Bearer $OPENAI_API_KEY\"",
                }
                suggestions = [
                    'Your server could not reach the OpenAI endpoint (TCP timeout). Common causes: local firewall, corporate network proxy, ISP filtering, or IPv6 routing problems.',
                    'Quick test: force IPv4 and check connectivity using curl (example): ' + example_curl['ipv4'],
                    'If IPv4 works but IPv6 does not, consider forcing IPv4 or disabling IPv6 on the server/network, or use a VPN.',
                    'If your network requires a proxy, set HTTPS_PROXY/HTTP_PROXY environment variables for the Flask process.',
                    'Alternatively try from another network (mobile hotspot) or use a VPN to confirm whether it is an ISP/network issue.'
                ]
                return jsonify({
                    'error': 'OpenAI call failed: Request timed out',
                    'detail': msg,
                    'suggestions': suggestions,
                    'curl_examples': example_curl
                }), 504

            return jsonify({'error': f'OpenAI call failed: {msg}', 'detail': msg}), 502

        if not translated:
            return jsonify({'error': 'No translation received from model'}), 502

        return jsonify({'translated': translated}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@note_bp.route('/notes/<int:note_id>/translate', methods=['POST'])
def translate_note(note_id):
    """Translate a note's content using the configured OpenAI-compatible endpoint.

    Request JSON: { "target_lang": "zh" } or { "target_lang": "en" }
    Returns: { translated: "..." }
    """
    try:
        data = request.json
        if not data or 'target_lang' not in data:
            return jsonify({'error': 'target_lang is required'}), 400

        target = data['target_lang']
        note = Note.query.get_or_404(note_id)

        # Use shared translate_text helper which encapsulates client selection.
        try:
            translated = translate_text(note.content or '', target)
        except RuntimeError as re:
            # Likely cause: no API key configured
            msg = str(re)
            return jsonify({
                'error': 'OpenAI call failed: No API key configured',
                'detail': msg,
                'suggestions': [
                    'Set OPENAI_API_KEY in the environment or create a .env file with OPENAI_API_KEY=sk-...',
                    'For quick local testing without a key, set MOCK_TRANSLATION=1 in your environment (development only).',
                    'If you intended to call GitHub-hosted models, set GITHUB_TOKEN and optionally BASE_URL.'
                ]
            }), 500
        except Exception as e:
            import traceback
            traceback.print_exc()
            msg = str(e)
            low = msg.lower()
            if 'timeout' in low or 'timed out' in low or 'connect' in low:
                example_curl = {
                    'ipv4': "curl --ipv4 -v https://api.openai.com/v1/models -H \"Authorization: Bearer $OPENAI_API_KEY\"",
                    'post_example': "curl --ipv4 -s -X POST https://api.openai.com/v1/chat/completions -H \"Authorization: Bearer $OPENAI_API_KEY\" -H \"Content-Type: application/json\" -d '{\"model\":\"gpt-4.1-mini\",\"messages\": [{\"role\":\"user\",\"content\":\"Say hi in Chinese\"}]}'"
                }
                suggestions = [
                    'Your server could not reach the OpenAI endpoint (TCP timeout). Common causes: local firewall, corporate network proxy, ISP filtering, or IPv6 routing problems.',
                    'Quick test: force IPv4 and check connectivity using curl (example): ' + example_curl['ipv4'],
                    'If IPv4 works but IPv6 does not, consider forcing IPv4 or disabling IPv6 on the server/network, or use a VPN.',
                    'If your network requires a proxy, set HTTPS_PROXY/HTTP_PROXY environment variables for the Flask process.',
                    'Alternatively try from another network (mobile hotspot) or use a VPN to confirm whether it is an ISP/network issue.'
                ]
                return jsonify({
                    'error': 'OpenAI call failed: Request timed out',
                    'detail': msg,
                    'suggestions': suggestions,
                    'curl_examples': example_curl
                }), 504

            return jsonify({'error': f'OpenAI call failed: {msg}', 'detail': msg}), 502

        if not translated:
            return jsonify({'error': 'No translation received from model'}), 502

        return jsonify({'translated': translated}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

