using System.Collections;
using System.Collections.Generic;
using System;
using System.Linq;
using System.IO;
using UnityEngine;
#if UNITY_EDITOR
using UnityEditor;
#endif

/**
 * todo
 *	- deleting pasted meshes will leak in editor (but adding a DestroyImmediate will break Undo...)
 *	- handle multiple selected meshes (by merging to a single mesh w/ transforms applied)?
 *	- support importing materials, bone weights, uvs
 */

namespace Parabox.OD
{
	/**
	 * OD file import & export.
	 */
	public static class CopyPaste
	{
		// When copying a mesh from Unity, should the mesh handedness be converted to right handed?
		public const string ConvertHandednessOnCopy = "od_ConvertToRightHandedOnCopy";
		// When pasting a mesh into Unity, should the mesh be converted from right handed coordinates to left?
		public const string ConvertHandednessOnPaste = "od_ConvertToLeftHandedOnPaste";
		// When pasting a mesh into Unity, should the mesh edges be split and normals recalculated?
		public const string SplitVerticesOnPaste = "od_SplitVerticesOnPaste";

		// Swap handed-ness on export?
		private static bool CopyConvertsHandedness
		{
			get
			{
#if UNITY_EDITOR
				return EditorPrefs.GetBool(ConvertHandednessOnCopy, false);
#else
				return false;
#endif
			}
		}

		// Swap handed-ness on import?
		private static bool PasteConvertsHandedness
		{
			get
			{
#if UNITY_EDITOR
				return EditorPrefs.GetBool(ConvertHandednessOnPaste, false);
#else
				return false;
#endif
			}
		}

		// Split vertices on import?
		private static bool SplitVertices
		{
			get
			{
#if UNITY_EDITOR
				return EditorPrefs.GetBool(SplitVerticesOnPaste, true);
#else
				return true;
#endif
			}
		}

		/**
		 * todo documentation
		 */
		private enum MeshAttribute
		{
			Position,
			Normal,
			Polygon,
			Weight,
			Morph,
			Uv,
			Null
		}

		/**
		 *	Get path to the OD Vertex Data temp file.
		 */
		public static string GetTempFile()
		{
			return string.Format("{0}ODVertexData.txt", Path.GetTempPath());
		}

		/**
		 *	Import from ODVertexData file.
		 */
		public static bool Import(string path, out Mesh mesh, out string[] materials)
		{
			MeshAttribute attrib = MeshAttribute.Null;
			List<Vector3> positions = new List<Vector3>();
			List<Vector3> normals = new List<Vector3>();
			List<Polygon> polygons = new List<Polygon>();
			List<UVCoord> uvs = new List<UVCoord>();

			using (StreamReader reader = new StreamReader(path))
			{
				for(string line = reader.ReadLine(); line != null; line = reader.ReadLine())
				{
					int attributeCount = TryParseAttrib(line, ref attrib);

					if(attributeCount > -1)
						continue;

					if(attrib == MeshAttribute.Position)
						TryParseVector3(line, positions);
					else if(attrib == MeshAttribute.Normal)
						TryParseVector3(line, normals);
					else if(attrib == MeshAttribute.Uv)
						TryParseUv(line, uvs);
					else if(attrib == MeshAttribute.Polygon)
						TryParsePolygon(line, polygons);
				}
			}

			mesh = new Mesh();
			mesh.name = "ODCopyPaste_Mesh";

			bool hasNormals = normals.Count == positions.Count;

			if(PasteConvertsHandedness)
			{
				for(int i = 0; i < positions.Count; i++)
				{
					// todo More options for swapping coordinate systems around (eg, max w/ z up)
					positions[i] = new Vector3(-positions[i].x, positions[i].y, positions[i].z);

					if(hasNormals)
						normals[i] = new Vector3(-normals[i].x, normals[i].y, normals[i].z);
				}
			}

			// If normals aren't present then this mesh is probably sharing vertex positions, so split them up and
			// recalculate hard edges.
			if (SplitVertices || !hasNormals)
			{
				MeshUtility.GeneratePerTriangleMesh(positions, uvs, polygons, ref mesh);
				mesh.RecalculateNormals();
			}
			else
			{
				mesh.vertices = positions.ToArray();
				int[] triangles = polygons.SelectMany(x => x.GetTriangles()).ToArray();
				mesh.triangles = triangles;
				mesh.normals = normals.ToArray();
			}

			mesh.RecalculateTangents();
			mesh.RecalculateBounds();
			materials = new string[]
			{
				polygons.First().material
			};

			return true;
		}

		// Copy mesh
		public static void Export(Mesh m, Material[] sharedMaterials)
		{
			if(m == null)
				return;

			int polyCount = 0;

			for (int i = 0; i < m.subMeshCount; i++)
			{
				MeshTopology topo = m.GetTopology(i);
				if (topo == MeshTopology.Triangles)
					polyCount += (int) m.GetIndexCount(i) / 3;
				else if(topo == MeshTopology.Quads)
					polyCount += (int) m.GetIndexCount(i) / 4;
				else
					return;
			}

			using (StreamWriter sw = new StreamWriter(GetTempFile(), false))
			{
				Vector3[] positions = m.vertices;
				Vector3[] normals = m.normals;

				sw.WriteLine(string.Format("VERTICES:{0}", m.vertexCount));

				foreach(Vector3 p in positions)
					sw.WriteLine(string.Format("{0} {1} {2}", CopyConvertsHandedness ? -p.x : p.x, p.y, p.z));

				if (normals != null)
				{
					sw.WriteLine(string.Format("VERTEXNORMALS:{0}", m.vertexCount));

					foreach(Vector3 n in normals)
						sw.WriteLine(string.Format("{0} {1} {2}", CopyConvertsHandedness ? -n.x : n.x, n.y, n.z));
				}

				for (int i = 0; i < m.subMeshCount; i++)
				{
					sw.WriteLine(string.Format("POLYGONS:{0}", polyCount));

					Material material = sharedMaterials != null && sharedMaterials.Length > 0
						? sharedMaterials[i % sharedMaterials.Length]
						: null;

					switch (m.GetTopology(i))
					{
						case MeshTopology.Triangles:
							int[] tris = m.GetIndices(i);
							for (int t = 0; t < tris.Length; t += 3)
								sw.WriteLine(string.Format(
									CopyConvertsHandedness
									? "{2},{1},{0};;{3};;FACE"
									: "{0},{1},{2};;{3};;FACE",
									tris[t],
									tris[t + 1],
									tris[t + 2],
									material == null ? "Default" : material.name));
							break;

						case MeshTopology.Quads:
							int[] quads = m.GetIndices(i);
							for (int t = 0; t < quads.Length; t += 4)
								sw.WriteLine(string.Format(
									CopyConvertsHandedness
									? "{3},{2},{1},{0};;{4};;FACE"
									: "{0},{1},{2},{3};;{4};;FACE",
									quads[t],
									quads[t + 1],
									quads[t + 2],
									quads[t + 3],
									material == null ? "Default" : material.name));
							break;

						default:
							// how'd you get here?
							break;
					}
				}
			}
		}

		private static int TryParseAttrib(string line, ref MeshAttribute attrib)
		{
			if(line.StartsWith("VERTICES"))
				attrib = MeshAttribute.Position;
			else if(line.StartsWith("VERTEXNORMALS"))
				attrib = MeshAttribute.Normal;
			else if(line.StartsWith("POLYGONS"))
				attrib = MeshAttribute.Polygon;
			else if(line.StartsWith("WEIGHT"))
				attrib = MeshAttribute.Weight;
			else if(line.StartsWith("MORPH"))
				attrib = MeshAttribute.Morph;
			else if(line.StartsWith("UV"))
				attrib = MeshAttribute.Uv;
			else
				return -1;

			string[] split = line.Split(':');

			int size = 0;

			int.TryParse(split[split.Length - 1], out size);

			return size;
		}

		private static bool TryParseUv(string line, List<UVCoord> uvs)
		{
			try
			{
				// 0.1725558042526245 0.5939202904701233:PLY:0:PNT:1
				// or
				// 0.1725558042526245 0.5939202904701233:PNT:1
				string[] all = line.Split(':');
				string[] coords = all[0].Split(' ');

				Vector2 pos;
				float.TryParse(coords[0], out pos.x);
				float.TryParse(coords[1], out pos.y);

				int plyIndex = -1, pntIndex = -1;

				// pnt index is always there
				int.TryParse(all[all.Length-1], out pntIndex);

				if (all.Length == 5 && all[1].StartsWith("PLY"))
					int.TryParse(all[2], out plyIndex);

				uvs.Add(new UVCoord() { position = pos, polygonIndex = plyIndex, vertexIndex = pntIndex });

				return true;
			}
			catch
			{
				return false;
			}
		}

		private static bool TryParseVector3(string line, List<Vector3> positions)
		{
			try
			{
				string[] split = line.Trim().Split(' ');
				Vector3 v;
				float.TryParse(split[0], out v.x);
				float.TryParse(split[1], out v.y);
				float.TryParse(split[2], out v.z);
				positions.Add(v);
			}
			catch
			{
				return false;
			}

			return true;
		}

		private static bool TryParsePolygon(string line, List<Polygon> polygons)
		{
			string[] POLYGON_SEPARATOR = new string[] { ";;" };

			try
			{
				// Comma separated list of each vertid in the polygon;;materialname;;polytype.
				// (which can be FACE, SubD, or CCSS)
				// 0,1,2,3;;Default;;FACE
				//
				// For now paste only supports PolyType Face
				string[] split = line.Split(POLYGON_SEPARATOR, StringSplitOptions.RemoveEmptyEntries);

				if(split[2].Equals("FACE"))
				{
					string[] face = split[0].Split(',');
					int[] indices = new int[face.Length];

					for(int i = 0; i < face.Length; i++)
						int.TryParse(face[i], out indices[i]);

					polygons.Add(new Polygon(split[1], indices));
				}
			}
			catch(Exception e)
			{
				Debug.LogError(e.ToString());
				return false;
			}

			return true;
		}
	}
}
