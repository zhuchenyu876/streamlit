import json
import ssl
import traceback
import logging
from websockets.sync.client import connect
import requests
import time
import threading
import socket

class TimeoutError(Exception):
    """Exception raised when a function times out."""
    pass

class Client:
    def __init__(self, url: str, username: str, robot_key: str, robot_token: str, retry_secs: int = 3, base_url: str = "https://agents.dyna.ai"):
        """
        Initialize client with WebSocket support
        
        Args:
            url: WebSocket URL (wss:// or ws://)
            username: username for authentication
            robot_key: Robot Key (Robot ID)
            robot_token: Robot Token
            retry_secs: Retry interval in seconds
            base_url: Base URL for API requests
        """
        # Convert url to string to handle any type conversion issues
        url = str(url) if url is not None else ""
        self.is_wss = url.startswith("wss://")
        self.url = url
        self.base_url = base_url
        
        # Configure SSL context for secure WebSocket
        if self.is_wss:
            self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE
        else:
            self.ssl_context = None
            
        self.username = username
        self.robot_key = robot_key
        self.robot_token = robot_token
        self.retry_secs = retry_secs
        self.segment_code = None
        self.current_group = None
        self.current_session_id = None

    def create_segment_code(self, group=None):
        """Create a new segment code for conversation context"""
        # Update session ID if group changes
        if group != self.current_group:
            self.current_group = group
            self.current_session_id = f"session_{int(time.time())}"
            
        url = f"{self.base_url}/openapi/v1/conversation/segment/create/"
        body = {
            "username": self.username,
            "cybertron_robot_key": self.robot_key,
            "cybertron_robot_token": self.robot_token,
        }
        try:
            response = requests.post(url=url, json=body)
            response.raise_for_status()
            result = response.json()
            if result.get('code') == '000000':
                self.segment_code = result.get('data', {}).get('segment_code')
                logging.info(f"Created new segment_code: {self.segment_code}")
                return self.segment_code
            else:
                logging.error(f"Failed to create segment_code: {result}")
                return None
        except Exception as e:
            logging.error(f"Error creating segment_code: {str(e)}")
            return None

    def get_current_session_id(self):
        """Get current session ID"""
        return self.current_session_id

    def send_msg(self, ws, question: str):
        """Send message through WebSocket with segment_code"""
        if not self.segment_code:
            self.create_segment_code()
            
        message = {
            "cybertron_robot_key": self.robot_key,
            "cybertron_robot_token": self.robot_token,
            "question": question,
            "username": self.username,
            "segment_code": self.segment_code
        }
        logging.debug(f"Sending message: {message}")
        ws.send(json.dumps(message))

    def receive_msg(self, ws):
        """Receive message from WebSocket"""
        message = ws.recv()
        try:
            message_json = json.loads(message)
            return message_json
        except Exception:
            logging.error(f"Error receiving message: \n{traceback.format_exc()}")
            return {}

    def websocket_chat_with_timeout(self, question: str, timeout: int = 40):
        """
        Run websocket_chat with a timeout
        """
        result = ["Request failed: Timeout after 40 seconds"]
        
        def target():
            nonlocal result
            try:
                result[0] = self.websocket_chat(question)
            except Exception as e:
                result[0] = f"Request failed: {str(e)}"
        
        # Create and start the thread
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        
        # Wait for the thread to complete or timeout
        thread.join(timeout)
        if thread.is_alive():
            return "Request failed: Timeout after 40 seconds"
        
        return result[0]

    def websocket_chat_with_timeout_and_timing(self, question: str, timeout: int = 40, record_timing: bool = True):
        """
        Run websocket_chat_with_timing with a timeout
        
        Args:
            question: The question to ask
            timeout: Timeout in seconds
            record_timing: Whether to record timing information
            
        Returns:
            Dict containing answer and timing information
        """
        result = [{
            'answer': f"Request failed: Timeout after {timeout} seconds",
            'first_token_response_time': None,
            'total_response_time': None,
            'attempt': 1
        }]
        
        def target():
            nonlocal result
            try:
                result[0] = self.websocket_chat_with_timing(question, record_timing=record_timing)
            except Exception as e:
                result[0] = {
                    'answer': f"Request failed: {str(e)}",
                    'first_token_response_time': None,
                    'total_response_time': None,
                    'attempt': 1
                }
        
        # Create and start the thread
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        
        # Wait for the thread to complete or timeout
        thread.join(timeout)
        if thread.is_alive():
            return {
                'answer': f"Request failed: Timeout after {timeout} seconds",
                'first_token_response_time': None,
                'total_response_time': None,
                'attempt': 1
            }
        
        return result[0]

    def websocket_chat(self, question: str, max_retries: int = 3) -> str:
        """
        Send question and receive answer using WebSocket connection
        
        Args:
            question: The question to ask
            max_retries: Maximum number of connection retry attempts
            
        Returns:
            Answer text or error message
        """
        result = self.websocket_chat_with_timing(question, max_retries, record_timing=False)
        return result['answer']
    
    def websocket_chat_with_timing(self, question: str, max_retries: int = 3, record_timing: bool = True) -> dict:
        """
        Send question and receive answer using WebSocket connection with timing information
        
        Args:
            question: The question to ask
            max_retries: Maximum number of connection retry attempts
            record_timing: Whether to record timing information
            
        Returns:
            Dict containing answer and timing information
        """
        # Create a new segment code for this chat if needed
        if not self.segment_code:
            self.create_segment_code()
            
        attempt = 0
        while attempt < max_retries:
            try:
                # Create SSL context if needed
                ssl_context = None
                if self.is_wss:
                    ssl_context = ssl.create_default_context()
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE
                
                # Connect to WebSocket server with a custom timeout
                # Note: connect() doesn't accept a timeout parameter directly
                # We'll rely on the thread-based timeout in websocket_chat_with_timeout
                with connect(self.url, ssl_context=ssl_context) as websocket:
                    # Record start time
                    start_time = time.time() if record_timing else None
                    
                    # Send the question
                    self.send_msg(websocket, question)
                    
                    # Receive and process response
                    receive_message = ""
                    receive_count = 0
                    use_send_again = False
                    first_response_time = None
                    
                    while True:
                        receive_count += 1
                        message_json = self.receive_msg(websocket)
                        
                        if not message_json:
                            if receive_count > 5:  # Prevent infinite loop
                                break
                            continue
                            
                        # Skip system messages
                        if message_json.get("index") in [-1, -2]:
                            continue
                            
                        msg_type = message_json.get("type")
                        
                        # Process string type messages
                        if msg_type == "string":
                            if message_json.get("index") not in [-1, -2]:
                                if message_json.get('code') == "000000":
                                    _message = message_json.get("data", "")
                                    
                                    # Record first response time
                                    if record_timing and first_response_time is None and _message and start_time is not None:
                                        first_response_time = time.time() - start_time
                                    
                                    receive_message += _message

                            if message_json.get("finish") == "y" or receive_count > 100:
                                break
                                
                        # Process JSON type messages
                        elif msg_type == "json":
                            if message_json.get('code') == "000000":
                                answer = message_json.get("data", {}).get("answer", {})
                                if not isinstance(answer, str):
                                    receive_message = json.dumps(answer, ensure_ascii=False)
                                else:
                                    receive_message = answer
                                
                                # Record first response time for JSON responses
                                if record_timing and first_response_time is None and receive_message and start_time is not None:
                                    first_response_time = time.time() - start_time
                            break
                            
                        # Process flow type messages
                        elif msg_type == "flow":
                            if message_json.get('code') == "000000":
                                if message_json["data"].get('final') is True:
                                    # Check if answer is a flow_jump
                                    if message_json["data"].get('answer', "").startswith("flow_jump"):
                                        use_send_again = True
                                        break
                                    else:
                                        flow_answer = message_json["data"].get('answer', "")
                                        
                                        # Record first response time for flow responses
                                        if record_timing and first_response_time is None and flow_answer and start_time is not None:
                                            first_response_time = time.time() - start_time
                                        
                                        receive_message += flow_answer

                                if message_json['data'].get('node_answer_finish') == "y" or receive_count > 100:
                                    break
                    
                    # Handle flow jump if needed
                    if use_send_again:
                        self.send_msg(websocket, "")
                        receive_message = ""
                        receive_count = 0
                        
                        while True:
                            receive_count += 1
                            message_json = self.receive_msg(websocket)
                            
                            if not message_json:
                                if receive_count > 5:
                                    break
                                continue
                                
                            if message_json.get("index") in [-1, -2]:
                                continue
                                
                            msg_type = message_json.get("type")
                            
                            if msg_type == "string":
                                if message_json.get("index") not in [-1, -2] and message_json.get('code') == "000000":
                                    receive_message += message_json.get("data", "")
                                if message_json.get("finish") == "y" or receive_count > 100:
                                    break
                                    
                            elif msg_type == "json":
                                if message_json.get('code') == "000000":
                                    answer = message_json.get("data", {}).get("answer", {})
                                    if not isinstance(answer, str):
                                        receive_message = json.dumps(answer, ensure_ascii=False)
                                    else:
                                        receive_message = answer
                                break
                                
                            elif msg_type == "flow":
                                if message_json.get('code') == "000000":
                                    if message_json["data"].get('answer') == "flow_jump":
                                        continue
                                    if message_json["data"].get('final') is True:
                                        receive_message += message_json["data"].get('answer', "")
                                    if message_json['data'].get('node_answer_finish') == "y" or receive_count > 100:
                                        break
                
                # Calculate total response time
                total_response_time = time.time() - start_time if start_time is not None else None
                
                # Return result with timing information
                return {
                    'answer': receive_message,
                    'first_token_response_time': first_response_time,
                    'total_response_time': total_response_time,
                    'attempt': attempt + 1
                }
                
            except Exception as e:
                attempt += 1
                error_msg = f"WebSocket chat error (attempt {attempt}/{max_retries}): {str(e)}"
                logging.error(error_msg)
                if attempt >= max_retries:
                    return {
                        'answer': f"Request failed after {max_retries} attempts: {str(e)}",
                        'first_token_response_time': None,
                        'total_response_time': None,
                        'attempt': attempt
                    }
                time.sleep(self.retry_secs)
        
        return {
            'answer': "Failed to get response after multiple attempts",
            'first_token_response_time': None,
            'total_response_time': None,
            'attempt': max_retries
        }