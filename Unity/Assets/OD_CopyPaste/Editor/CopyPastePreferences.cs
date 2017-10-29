using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;

namespace Parabox.OD
{
	public static class CopyPastePreferences
	{
		private static bool m_Initialized = false;
		private static bool m_ConvertToRightHandedOnCopy;
		private static bool m_ConvertToLeftHandedOnPaste;
		private static bool m_SplitVerticesOnPaste;

		private static GUIContent m_SplitVerticesContent = new GUIContent("Split Vertices on Paste", "When enabled pasted meshes will always be constructed with hard edges instead of importing this value from the existing normals and uvs.");

		private static void InitializePreferences()
		{
			m_ConvertToRightHandedOnCopy = EditorPrefs.GetBool(CopyPaste.ConvertHandednessOnCopy, false);
			m_ConvertToLeftHandedOnPaste = EditorPrefs.GetBool(CopyPaste.ConvertHandednessOnPaste, false);
			m_SplitVerticesOnPaste = EditorPrefs.GetBool(CopyPaste.SplitVerticesOnPaste, false);
			m_Initialized = true;
		}

		[PreferenceItem("OD Copy Paste")]
		private static void OnGUI()
		{
			if(!m_Initialized)
				InitializePreferences();

			EditorGUI.BeginChangeCheck();

			GUILayout.Label("Copy", EditorStyles.boldLabel);
			m_ConvertToRightHandedOnCopy = EditorGUILayout.Toggle("Convert To Right Handed", m_ConvertToRightHandedOnCopy);
			GUILayout.Label("Paste", EditorStyles.boldLabel);
			m_ConvertToLeftHandedOnPaste = EditorGUILayout.Toggle("Convert To Left Handed", m_ConvertToLeftHandedOnPaste);
			m_SplitVerticesOnPaste = EditorGUILayout.Toggle(m_SplitVerticesContent, m_SplitVerticesOnPaste);

			if(EditorGUI.EndChangeCheck())
			{
				EditorPrefs.SetBool(CopyPaste.ConvertHandednessOnCopy, m_ConvertToRightHandedOnCopy);
				EditorPrefs.SetBool(CopyPaste.ConvertHandednessOnPaste, m_ConvertToLeftHandedOnPaste);
				EditorPrefs.SetBool(CopyPaste.SplitVerticesOnPaste, m_SplitVerticesOnPaste);
			}
		}
	}
}
