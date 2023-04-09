# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import chat_pb2 as chat__pb2


class ChatServerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ChatStream = channel.unary_stream(
                '/grpc.ChatServer/ChatStream',
                request_serializer=chat__pb2.ConnectRequest.SerializeToString,
                response_deserializer=chat__pb2.ConnectReply.FromString,
                )
        self.SendMessage = channel.unary_unary(
                '/grpc.ChatServer/SendMessage',
                request_serializer=chat__pb2.MessageRequest.SerializeToString,
                response_deserializer=chat__pb2.MessageReply.FromString,
                )
        self.Signup = channel.unary_unary(
                '/grpc.ChatServer/Signup',
                request_serializer=chat__pb2.SignupRequest.SerializeToString,
                response_deserializer=chat__pb2.SignupReply.FromString,
                )
        self.Login = channel.unary_unary(
                '/grpc.ChatServer/Login',
                request_serializer=chat__pb2.LoginRequest.SerializeToString,
                response_deserializer=chat__pb2.LoginReply.FromString,
                )
        self.Logout = channel.unary_unary(
                '/grpc.ChatServer/Logout',
                request_serializer=chat__pb2.LogoutRequest.SerializeToString,
                response_deserializer=chat__pb2.LogoutReply.FromString,
                )
        self.List = channel.unary_unary(
                '/grpc.ChatServer/List',
                request_serializer=chat__pb2.ListRequest.SerializeToString,
                response_deserializer=chat__pb2.ListReply.FromString,
                )
        self.Delete = channel.unary_unary(
                '/grpc.ChatServer/Delete',
                request_serializer=chat__pb2.DeleteRequest.SerializeToString,
                response_deserializer=chat__pb2.DeleteReply.FromString,
                )
        self.IsMasterQuery = channel.unary_unary(
                '/grpc.ChatServer/IsMasterQuery',
                request_serializer=chat__pb2.IsMasterRequest.SerializeToString,
                response_deserializer=chat__pb2.IsMasterReply.FromString,
                )
        self.AddConnect = channel.unary_unary(
                '/grpc.ChatServer/AddConnect',
                request_serializer=chat__pb2.AddConnectRequest.SerializeToString,
                response_deserializer=chat__pb2.AddConnectReply.FromString,
                )
        self.Commit = channel.unary_unary(
                '/grpc.ChatServer/Commit',
                request_serializer=chat__pb2.CommitRequest.SerializeToString,
                response_deserializer=chat__pb2.CommitReply.FromString,
                )


class ChatServerServicer(object):
    """Missing associated documentation comment in .proto file."""

    def ChatStream(self, request, context):
        """request-stream setup to send requests, then continuously receive reply
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendMessage(self, request, context):
        """rpc ServStream (ServConnectRequest) returns (stream ServConnectReply); 
        other functions are simple RPCs
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Signup(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Login(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Logout(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def List(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Delete(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def IsMasterQuery(self, request, context):
        """replication edit
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AddConnect(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Commit(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ChatServerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'ChatStream': grpc.unary_stream_rpc_method_handler(
                    servicer.ChatStream,
                    request_deserializer=chat__pb2.ConnectRequest.FromString,
                    response_serializer=chat__pb2.ConnectReply.SerializeToString,
            ),
            'SendMessage': grpc.unary_unary_rpc_method_handler(
                    servicer.SendMessage,
                    request_deserializer=chat__pb2.MessageRequest.FromString,
                    response_serializer=chat__pb2.MessageReply.SerializeToString,
            ),
            'Signup': grpc.unary_unary_rpc_method_handler(
                    servicer.Signup,
                    request_deserializer=chat__pb2.SignupRequest.FromString,
                    response_serializer=chat__pb2.SignupReply.SerializeToString,
            ),
            'Login': grpc.unary_unary_rpc_method_handler(
                    servicer.Login,
                    request_deserializer=chat__pb2.LoginRequest.FromString,
                    response_serializer=chat__pb2.LoginReply.SerializeToString,
            ),
            'Logout': grpc.unary_unary_rpc_method_handler(
                    servicer.Logout,
                    request_deserializer=chat__pb2.LogoutRequest.FromString,
                    response_serializer=chat__pb2.LogoutReply.SerializeToString,
            ),
            'List': grpc.unary_unary_rpc_method_handler(
                    servicer.List,
                    request_deserializer=chat__pb2.ListRequest.FromString,
                    response_serializer=chat__pb2.ListReply.SerializeToString,
            ),
            'Delete': grpc.unary_unary_rpc_method_handler(
                    servicer.Delete,
                    request_deserializer=chat__pb2.DeleteRequest.FromString,
                    response_serializer=chat__pb2.DeleteReply.SerializeToString,
            ),
            'IsMasterQuery': grpc.unary_unary_rpc_method_handler(
                    servicer.IsMasterQuery,
                    request_deserializer=chat__pb2.IsMasterRequest.FromString,
                    response_serializer=chat__pb2.IsMasterReply.SerializeToString,
            ),
            'AddConnect': grpc.unary_unary_rpc_method_handler(
                    servicer.AddConnect,
                    request_deserializer=chat__pb2.AddConnectRequest.FromString,
                    response_serializer=chat__pb2.AddConnectReply.SerializeToString,
            ),
            'Commit': grpc.unary_unary_rpc_method_handler(
                    servicer.Commit,
                    request_deserializer=chat__pb2.CommitRequest.FromString,
                    response_serializer=chat__pb2.CommitReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'grpc.ChatServer', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ChatServer(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def ChatStream(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/grpc.ChatServer/ChatStream',
            chat__pb2.ConnectRequest.SerializeToString,
            chat__pb2.ConnectReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SendMessage(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/grpc.ChatServer/SendMessage',
            chat__pb2.MessageRequest.SerializeToString,
            chat__pb2.MessageReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Signup(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/grpc.ChatServer/Signup',
            chat__pb2.SignupRequest.SerializeToString,
            chat__pb2.SignupReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Login(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/grpc.ChatServer/Login',
            chat__pb2.LoginRequest.SerializeToString,
            chat__pb2.LoginReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Logout(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/grpc.ChatServer/Logout',
            chat__pb2.LogoutRequest.SerializeToString,
            chat__pb2.LogoutReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def List(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/grpc.ChatServer/List',
            chat__pb2.ListRequest.SerializeToString,
            chat__pb2.ListReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Delete(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/grpc.ChatServer/Delete',
            chat__pb2.DeleteRequest.SerializeToString,
            chat__pb2.DeleteReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def IsMasterQuery(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/grpc.ChatServer/IsMasterQuery',
            chat__pb2.IsMasterRequest.SerializeToString,
            chat__pb2.IsMasterReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def AddConnect(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/grpc.ChatServer/AddConnect',
            chat__pb2.AddConnectRequest.SerializeToString,
            chat__pb2.AddConnectReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Commit(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/grpc.ChatServer/Commit',
            chat__pb2.CommitRequest.SerializeToString,
            chat__pb2.CommitReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
