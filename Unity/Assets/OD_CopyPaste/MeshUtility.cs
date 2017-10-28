using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace Parabox.OD
{
	public static class MeshUtility
	{
		public static int[] TriangulatePolygon(Polygon poly)
		{
			return TriangulatePolygon(poly.indices);
		}

		public static int[] TriangulatePolygon(int[] indices)
		{
			// for now just do a simple fan triangulate
			// in the future it would be nice to do ear clipping
			int[] triangles = new int[(indices.Length - 2) * 3];

			for (int i = 1; i < indices.Length - 1; i++)
			{
				triangles[(i-1)*3+0] = indices[0  ];
				triangles[(i-1)*3+1] = indices[i  ];
				triangles[(i-1)*3+2] = indices[i+1];
			}

			return triangles;
		}

		public static void GeneratePerTriangleMesh(List<Vector3> positions,
			List<UVCoord> uvCoords,
			List<Polygon> polygons,
			ref Mesh mesh)
		{
			List<int> triangles = new List<int>();
			List<Vector2> uvs = new List<Vector2>();
			bool uvsValid = uvCoords.Count > 0;
			bool uvsIndexedByPolygon = uvsValid && uvCoords.First().polygonIndex > -1;

			if (uvsIndexedByPolygon)
			{
				var polygonUvLookup = new Dictionary<int, Dictionary<int, Vector2>>();

				for (int i = 0, uc = uvCoords.Count; i < uc; i++)
				{
					Dictionary<int, Vector2> tri = null;

					if (polygonUvLookup.TryGetValue(uvCoords[i].polygonIndex, out tri))
						tri.Add(uvCoords[i].vertexIndex, uvCoords[i].position);
					else
						polygonUvLookup.Add(uvCoords[i].polygonIndex,
							new Dictionary<int, Vector2>() {{uvCoords[i].vertexIndex, uvCoords[i].position}});
				}

				for (int ply = 0, tc = polygons.Count; ply < tc; ply++)
				{
					int[] indices = TriangulatePolygon(polygons[ply]);

					triangles.AddRange(indices);

					try
					{
						for (int n = 0, ic = indices.Length; uvsValid && n < ic; n++)
							uvs.Add(polygonUvLookup[ply][indices[n]]);
					}
					catch
					{
						uvsValid = false;
					}
				}
			}
			else
			{
				Dictionary<int, Vector2> uvLookup = new Dictionary<int, Vector2>();

				for(int i = 0, uc = uvCoords.Count; i < uc; i++)
					uvLookup.Add(uvCoords[i].vertexIndex, uvCoords[i].position);

				for (int i = 0, tc = polygons.Count; i < tc; i++)
				{
					int[] indices = TriangulatePolygon(polygons[i].indices);
					triangles.AddRange(indices);

					Vector2 v;

					foreach(int tri in indices)
						if(uvLookup.TryGetValue(tri, out v))
							uvs.Add(v);
				}

				uvsValid = uvs.Count == triangles.Count;
			}

			int triangleCount = triangles.Count;

			Vector3[] splitVertices = new Vector3[triangleCount];
			int[] splitTriangles = new int[triangleCount];

			for (int i = 0; i < triangleCount; i++)
			{
				splitVertices[i] = positions[triangles[i]];
				splitTriangles[i] = i;
			}

			if(mesh == null)
				mesh = new Mesh();
			else
				mesh.Clear();

			mesh.vertices = splitVertices;
			mesh.uv = uvsValid ? uvs.ToArray() : null;
			mesh.triangles = splitTriangles;
		}
	}
}
