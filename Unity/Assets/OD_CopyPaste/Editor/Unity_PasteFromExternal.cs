using UnityEngine;
using UnityEditor;
using System.IO;

namespace Parabox.OD
{
	/**
	 * Editor functionality for copy / paste from external.
	 */
	internal static class Unity_PasteFromExternalPaste
	{
		public static Material DefaultMaterial()
		{
			GameObject go = GameObject.CreatePrimitive(PrimitiveType.Cube);
			Material mat = go.GetComponent<MeshRenderer>().sharedMaterial;
			Object.DestroyImmediate(go);
			return mat;
		}

		[MenuItem("Edit/Paste From External to Scene %#v")]
		public static void Import()
		{
			Mesh m = OD_File.Import(OD_File.GetTempFile());

			GameObject go = new GameObject();
			go.AddComponent<MeshFilter>().sharedMesh = m;
			go.AddComponent<MeshRenderer>().sharedMaterial = DefaultMaterial();

		}
	}
}
