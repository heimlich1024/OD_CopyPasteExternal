using System.Collections;
using System.Collections.Generic;
using System;
using System.IO;
using UnityEngine;

namespace Parabox.OD
{
	/**
	 *	OD temp file import & export.
	 */
	public static class OD_File
	{
		/**
		 *	@todo
		 */
		public enum MeshAttribute
		{
			Position,
			Polygon,
			Weight,
			Morph,
			UV,
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
		public static Mesh Import(string path)
		{
			MeshAttribute attrib = MeshAttribute.Null;

			List<Vector3> positions = new List<Vector3>();
			List<int> polygons = new List<int>();

			using (StreamReader reader = new StreamReader(path))
			{
				for(string line = reader.ReadLine(); line != null; line = reader.ReadLine())
				{
					if(TryParse_Attrib(line, ref attrib))
						continue;

					if(attrib == MeshAttribute.Position)
						TryParse_Position(line, positions);
					else if(attrib == MeshAttribute.Polygon)
						TryParse_Polygon(line, polygons);
				}
			}

			Mesh m = new Mesh();
			m.vertices = positions.ToArray();
			m.triangles = polygons.ToArray();

			return m;
		}

		private static bool TryParse_Attrib(string line, ref MeshAttribute attrib)
		{
			if(line.StartsWith("VERTICES"))
				attrib = MeshAttribute.Position;
			else if(line.StartsWith("POLYGONS"))
				attrib = MeshAttribute.Polygon;
			else if(line.StartsWith("WEIGHT"))
				attrib = MeshAttribute.Weight;
			else if(line.StartsWith("MORPH"))
				attrib = MeshAttribute.Morph;
			else if(line.StartsWith("UV"))
				attrib = MeshAttribute.UV;
			else
				return false;

			return true;
		}

		private static bool TryParse_Position(string line, List<Vector3> positions)
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

		private static bool TryParse_Polygon(string line, List<int> polygons)
		{
			string[] POLYGON_SEPARATOR = new string[] { ";;" };

			try
			{
				// comma separate list of each vertid in the polygon;;materialname;;polytype
				// (which can be FACE, SubD, or CCSS)
				// 0,1,2,3;;Default;;FACE
				string[] split = line.Split(POLYGON_SEPARATOR, StringSplitOptions.RemoveEmptyEntries);

				if(split[2].Equals("FACE"))
				{
					string[] face = split[0].Split(',');

					for(int i = 0; i < face.Length; i += 2)
					{
						int a, b, c;
						int.TryParse(face[i+0], out a);
						int.TryParse(face[i+1], out b);
						int.TryParse(face[(i+2) % face.Length], out c);

						polygons.Add(a);
						polygons.Add(b);
						polygons.Add(c);
					}
				}
			}
			catch
			{
				return false;
			}

			return true;
		}
	}
}
