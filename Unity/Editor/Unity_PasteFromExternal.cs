using UnityEngine;
using UnityEditor;
using System.IO;

namespace Parabox.OD
{
	static class Unity_PasteFromExternal
	{
		public static Material DefaultMaterial()
		{
			GameObject go = GameObject.CreatePrimitive(PrimitiveType.Cube);
			Material mat = go.GetComponent<MeshRenderer>().sharedMaterial;
			GameObject.DestroyImmediate(go);
			return mat;
		}

		[MenuItem("Assets/Paste From External to Scene &d")]
		public static void Import()
		{
			Mesh m = OD_File.Import("Assets/ODVertexDataNGon.txt");
			// Mesh m = OD_File.Import("Assets/ODVertexData.txt");
			// Mesh m = OD_File.Import(OD_File.GetTempFile());

			GameObject go = new GameObject();
			go.AddComponent<MeshFilter>().sharedMesh = m;
			go.AddComponent<MeshRenderer>().sharedMaterial = DefaultMaterial();

		}
	}
}
