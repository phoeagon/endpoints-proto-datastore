import endpoints

from google.appengine.ext import ndb
from protorpc import remote

from endpoints_proto_datastore.ndb import EndpointsModel


class MyModel(EndpointsModel):
  attr1 = ndb.StringProperty()
  attr2 = ndb.StringProperty()
  created = ndb.DateTimeProperty(auto_now_add=True)


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
  # Since endpoints-proto-datastore doesn't provide a decorator to take
  # in a collection of some RPC Message as argument, we use the
  # endpoints.method decorator to manually specify the types.
  #
  # To get a ProtoRPC class that stores a collection of entities, use:
  #   EndpointsDecoratedModel.ProtoCollection()
  # To get a ProtoRPC class that stores an instance of that entity, use:
  #   EndpointsDecoratedModel.ProtoModel()
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
    # The advantage of using endpoints-proto-datastore API in this example
    # is that the corresponding ProtoRPC class is always up-to-date with
    # the NDB entity.


application = endpoints.api_server([MyApi], restricted=False)
