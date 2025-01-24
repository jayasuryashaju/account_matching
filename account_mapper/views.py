import os
import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import RawData
from .serializers import RawDataSerializer, InputRowSerializer
from .utils import get_best_match, combine_row
from django.core.files.storage import default_storage
from django.conf import settings
from django.core.exceptions import ValidationError
from .config import USE_COLUMNS, HIGH_THRESHOLD, LOW_THRESHOLD, DATABASE_COLUMNS
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
import tempfile




class MatchRowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Process a single row by combining and matching."""

        try:
            """
            Process a single row of new data by comparing it to combined RAM rows.
            """
            file = request.FILES.get("file")
            if file:
                try:
                    input_data = pd.read_excel(file)
                except Exception as e:
                    return Response({"error": f"Failed to read Excel file: {str(e)}"},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                # Check if JSON data is provided
                json_data = request.data.get("data")
                if json_data:
                    try:
                        input_data = pd.DataFrame(json_data)
                    except Exception as e:
                        return Response({"error": f"Failed to parse JSON data: {str(e)}"},
                                        status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"error": "No file or JSON data provided"}, status=status.HTTP_400_BAD_REQUEST)

            ram_data = pd.DataFrame(RawData.objects.all().values())
            print(ram_data.head())

            columns = USE_COLUMNS

            # Combine RAM rows
            print("Combining RAM rows from database...")
            ram_combined_rows = ram_data.apply(lambda row: combine_row(row, DATABASE_COLUMNS), axis=1)
            print(ram_combined_rows)

            # Add result columns to input data
            results = []
            scores = []

            print("Processing input rows...")
            for _, input_row in input_data.iterrows():
                input_combined_str = combine_row(input_row, columns)
                best_score, best_result = get_best_match(input_combined_str, ram_combined_rows, HIGH_THRESHOLD, LOW_THRESHOLD)
                results.append(best_result)
                scores.append(best_score)

            # Add results to input data
            input_data["Result"] = results
            input_data["Score"] = scores

            # Create a temporary file for the Excel output
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
                output_file_path = tmp_file.name
                input_data.to_excel(output_file_path, index=False)

            # Read the file and create a response
            with open(output_file_path, "rb") as file:
                response = HttpResponse(file.read(),
                                        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                response["Content-Disposition"] = f'attachment; filename="processed_data.xlsx"'
                return response

        except Exception as e:
            return Response({"error": f"Error processing file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

class UploadRawDataView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        # Check if a file is included in the request
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Save the uploaded file to a temporary location
        file_path = os.path.join(settings.MEDIA_ROOT, file.name)
        with default_storage.open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # Read the Excel file
        try:
            data = pd.read_excel(file_path)

            # Check that required columns exist
            required_columns = USE_COLUMNS
            if not all(col in data.columns for col in required_columns):
                return Response({"error": "Missing required columns in the uploaded file."},
                                 status=status.HTTP_400_BAD_REQUEST)

            # Loop through each row and save the data to the database
            for _, row in data.iterrows():
                try:
                    # Create and save the RawData instance
                    raw_data = RawData(
                        distributor_name = row['Distributor Name'],
                        retailer_name=row['Retailer Name'],
                        item_description=row['Item Description'],
                        street=row['Street'],
                        city=row['City'],
                        state=row['State'],
                        zip_code=row['Zip code']
                    )
                    raw_data.save()

                except ValidationError as e:
                    # If there is a validation error, handle it here
                    return Response({"error": f"Validation error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": f"Error reading the file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Remove the temporary file
        default_storage.delete(file_path)

        # Return success message
        return Response({"message": "File uploaded and processed successfully!"}, status=status.HTTP_200_OK)
