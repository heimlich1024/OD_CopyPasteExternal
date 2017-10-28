using UnityEngine;
using UnityEditor;
using System.IO;
using System.Linq;

namespace Parabox.OD
{
	/**
	 * Editor functionality for copy / paste from external.
	 */
	internal static class CopyPasteMenuItems
	{
		private static Material DefaultMaterial()
		{
			GameObject go = GameObject.CreatePrimitive(PrimitiveType.Cube);
			Material mat = go.GetComponent<MeshRenderer>().sharedMaterial;
			Object.DestroyImmediate(go);
			return mat;
		}

		[MenuItem("Edit/Paste Mesh from External %#v")]
		private static void Import()
		{
			Mesh m = CopyPaste.Import(CopyPaste.GetTempFile());

			GameObject go = new GameObject();
			go.AddComponent<MeshFilter>().sharedMesh = m;
			go.AddComponent<MeshRenderer>().sharedMaterial = DefaultMaterial();
		}

		[MenuItem("Edit/Copy Mesh To External %#c")]
		private static void Export()
		{
			GameObject first = Selection.gameObjects.FirstOrDefault(x => x.GetComponent<MeshFilter>() != null);

			if(first != null)
				CopyPaste.Export(
					first.GetComponent<MeshFilter>().sharedMesh,
					first.GetComponent<MeshRenderer>().sharedMaterials);
		}
	}
}
