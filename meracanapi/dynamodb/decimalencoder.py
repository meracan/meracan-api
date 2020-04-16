import decimal
import json


# This is a workaround for: http://bugs.python.org/issue16535
class DecimalEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, decimal.Decimal):
      n=float(obj)
      if n.is_integer():n=int(n)
      return n
    return super(DecimalEncoder, self).default(obj)