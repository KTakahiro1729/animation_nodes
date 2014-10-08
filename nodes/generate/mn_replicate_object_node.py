import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from mn_utils import *

class ObjectNamePropertyGroup(bpy.types.PropertyGroup):
	objectName = bpy.props.StringProperty(name = "Socket Name", default = "", update = nodePropertyChanged)

class ReplicateObjectNode(Node, AnimationNode):
	bl_idname = "ReplicateObjectNode"
	bl_label = "Replicate Object"
	
	objectNames = bpy.props.CollectionProperty(type = ObjectNamePropertyGroup)
	visibleObjectNames = bpy.props.CollectionProperty(type = ObjectNamePropertyGroup)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("ObjectSocket", "Object")
		self.inputs.new("IntegerSocket", "Instances")
		self.outputs.new("ObjectListSocket", "Objects")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		pass
		
	def execute(self, input):
		output = {}
		object = input["Object"]
		amount = max(input["Instances"], 0)
			
		while amount > len(self.visibleObjectNames):
			self.linkObjectToScene(object)
		while amount < len(self.visibleObjectNames):
			self.unlinkObjectFromScene()
			
		objects = []
		for i in range(amount):
			outputObject = bpy.data.objects.get(self.visibleObjectNames[i].objectName)
			if outputObject is not None:
				if outputObject.data != object.data:
					outputObject.data = object.data
				objects.append(outputObject)
			
		output["Objects"] = objects
		return output
		
	def free(self):
		while len(self.visibleObjectNames) > 0:
			self.unlinkObjectFromScene()
			
	def copy(self, node):
		self.objectNames.clear()
		self.visibleObjectNames.clear()
		
	def newInstance(self, object):
		newObject = bpy.data.objects.new(self.getPossibleInstanceName(), object.data)
		#newObject.parent = bpy.data.objects["Suzanne"]
		item = self.objectNames.add()
		item.objectName = newObject.name
		return object
	def getPossibleInstanceName(self, name = "instance"):
		counter = 1
		while bpy.data.objects.get(name + str(counter)) is not None:
			counter += 1
		return name + str(counter)
		
	def linkObjectToScene(self, object):
		if len(self.objectNames) == len(self.visibleObjectNames):
			self.newInstance(object)
		object = bpy.data.objects.get(self.objectNames[len(self.visibleObjectNames)].objectName)
		if object is None:
			self.objectNames.remove(len(self.visibleObjectNames))
		else:
			bpy.context.scene.objects.link(object)
			item = self.visibleObjectNames.add()
			item.objectName = object.name
	def unlinkObjectFromScene(self):
		if len(self.visibleObjectNames) > 0:
			object = bpy.data.objects.get(self.visibleObjectNames[-1].objectName)
			bpy.context.scene.objects.unlink(object)
			self.visibleObjectNames.remove(len(self.visibleObjectNames) - 1)
	
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)