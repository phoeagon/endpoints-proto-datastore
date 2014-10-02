import endpoints

from google.appengine.ext import ndb
from protorpc import remote

from endpoints_proto_datastore.ndb import EndpointsModel


# Same as in ../basic.
class MyModel(EndpointsModel):
  attr1 = ndb.StringProperty()
  attr2 = ndb.StringProperty()
  created = ndb.DateTimeProperty(auto_now_add=True)


# Use of this decorator is the same for APIs created with or without
# endpoints-proto-datastore.
@endpoints.api(name='myapi', version='v1', description='My Little API')
class MyApi(remote.Service):

  # Same as basic. Just for illustration purposes.
  @MyModel.method(path='mymodel', http_method='POST', name='mymodel.insert')
  def MyModelInsert(self, my_model):
    my_model.put()
    return my_model

  # Suppose we need to support batch insert for better performance,
  # We would want a "batch-insert" API.
  #
  # Since datastore-proto doesn't provide a batch insert, we do it by
  # wrapping the handler with a standard endpoints.method decorator.
  #
  # Meanwhile, we utilize datastore-proto to generate ProtoRPC classes
  # for us, such that we don't have to explicitly update them if the NDB
  # class is updated.
  #
  # To get a ProtoRPC class that stores a collection of entities, use:
  #   EndpointsDecoratedModel.ProtoCollection()
  # To get a ProtoRPC class that stores an instance of that entity, use:
  #   EndpointsDecoratedModel.ProtoModel()
  #
  # This handler illustrates how to write a custom handler with datastore-
  # proto generated classes as input/output, as well as conversion between
  # ndb entities & ProtoRPC messages.
  #
  @endpoints.method(MyModel.ProtoCollection(), # Input type: Collection of model.
                    MyModel.ProtoCollection(), # Return type: Collection of model.
                    path='mymodel_multi',
                    http_method='POST',
                    name='mymodel.insert_multi')
  def MyModelMultiInsert(self, items):
    # You may want to check authentication here, since user_required is not available.
    # .... (Omitted here)
    # Get a list of entities by converting the RPC Messages passed in into corresponding
    # NDB entities.
    entities = [MyModel.FromMessage(item_msg) for item_msg in items.items]
    # Call ndb.put_multi to actually write the entites to datastore.
    ndb.put_multi(entities)
    # Return an RPC Collection containing a list of inserted entities.
    items.items = [entity.ToMessage() for entity in entities]
    return items


# Same as basic.
application = endpoints.api_server([MyApi], restricted=False)
